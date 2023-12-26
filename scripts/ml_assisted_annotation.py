import os
import cv2
from tqdm import tqdm
from typing import List
from pathlib import Path
from os.path import join
from shutil import copy2
from copy import deepcopy
from natsort import natsorted
import xml.etree.ElementTree as ET

from src.ml.yolo.ball import BallDetector
from src.utilities.utils import BoundingBox
from notebooks.utils import Bbox, ImageAnnot
from src.ml.yolo.vb_action.action_detection import ActionDetector


class CVATDataset:
    def __init__(self, meta_file):
        self.annotations = self._initialize_meta(meta_file)

    @staticmethod
    def _initialize_meta(file):
        assert Path(file).is_file(), "file doesn't exist."
        meta = ET.parse(file)
        meta_root = deepcopy(meta.getroot())
        annotations = ET.Element('annotations')
        version = ET.SubElement(annotations, 'versions')
        version.text = '1.1'
        annotations.insert(1, meta_root)

        return annotations

    @staticmethod
    def add_bboxes(img_tag: ET.SubElement, yolo_bboxes: List[BoundingBox]):
        for bb in yolo_bboxes:
            x1, y1, x2, y2 = [str(i) for i in bb.box]
            _ = ET.SubElement(
                img_tag, 'box', label=bb.name, source='manual', occluded='0',
                xtl=x1, ytl=y1, xbr=x2, ybr=y2, z_order="0"
            )

    def create_img(self, name: str, width: int | str, height: int | str):
        return ET.SubElement(self.annotations, 'image', name=name, width=str(width), height=str(height))

    def output(self, filename: str):
        tree = ET.ElementTree(self.annotations)
        ET.indent(tree, space="\t", level=0)
        tree.write(filename)


class YoloDataset:
    def __init__(self, names):
        self.names = names
        self.names2labels, self.labels2names = self._init_labels(self.names)
        self.data_dir = 'data'
        self.obj_train_data_dir = 'obj_train_data'
        self.img_dir = join(self.data_dir, self.obj_train_data_dir)
        os.makedirs(self.img_dir, exist_ok=True)
        self.img_annots: List[ImageAnnot] = []

    def _init_labels(self, names):
        l2n = {}
        n2l = {}
        for i, item in enumerate(names):
            l2n[i] = item
            n2l[item] = i
        return n2l, l2n

    @staticmethod
    def create_img(img_path: Path):
        return ImageAnnot(img_path=img_path)

    def add_bboxes(self, img_annot: ImageAnnot, yolo_bboxes: List[BoundingBox]):
        for i, bb in enumerate(yolo_bboxes):
            bbox = Bbox(bb.box, self.names2labels[bb.name])
            img_annot.add_item(bbox)
        self.img_annots.append(img_annot)

    def output(self, output_dir):
        """
        prepare obj.data.
        prepare obj.names.
        prepare train.txt.
        """

        main_dir = join(output_dir, self.data_dir)
        os.makedirs(main_dir, exist_ok=True)

        obj_data_dir = join(main_dir, 'obj.data')
        obj_data = ""
        obj_data += f"classes = {len(self.names)}\n"
        obj_data += f"train = {join(output_dir, self.data_dir, 'train.txt')}\n"
        obj_data += f"names = {join(output_dir, self.data_dir, 'obj.names')}\n"
        obj_data += "backup = backup/"

        # Create obj.data
        with open(obj_data_dir, 'w') as f:
            f.write(obj_data)

        obj_names_dir = join(main_dir, "obj.names")
        obj_names = ''
        for i, item in enumerate(self.names):
            obj_names += f"{item}"
            if i != len(self.names) - 1:
                obj_names += "\n"

        # Create obj.names
        with open(obj_names_dir, 'w') as f:
            f.write(obj_names)

        train_data_dir = join(main_dir, self.obj_train_data_dir)
        train_txt_dir = join(main_dir, 'train.txt')
        os.makedirs(train_data_dir, exist_ok=True)
        train_txt = ''
        all_image_paths = [item.img_path for item in self.img_annots]

        for i, img in enumerate(all_image_paths):
            new_path = join(self.img_dir, img.name)
            abs_path = join(output_dir, self.img_dir)
            copy2(img.as_posix(), abs_path)
            train_txt += new_path
            if i != len(all_image_paths) - 1:
                train_txt += '\n'

        # Create train.txt
        with open(train_txt_dir, 'w') as output:
            output.write(train_txt)

        for img_annot in self.img_annots:
            with open(join(train_data_dir, img_annot.img_path.stem + '.txt'), 'w') as annotation:
                text = img_annot.get_yolo_format()
                annotation.write(text)


if __name__ == '__main__':
    action_cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/vb_actions_6_class/model1/weights/best.pt',
        "labels": {
            0: 'ball',
            1: 'block',
            2: 'receive',
            3: 'set',
            4: 'spike',
            5: 'serve'
        }
    }
    ball_cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/ball_segment/model2/weights/best.pt',
        "labels": {0: 'ball'}
    }

    action_detector = ActionDetector(action_cfg)
    ball_detector = BallDetector(ball_cfg)

    image_dir = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/4_classes/receive'
    images = natsorted(list(Path(image_dir).glob('*.png')))
    # meta_file = '/home/masoud/Desktop/projects/volleyball_analytics/notebooks/meta.xml'
    output_path = '/home/masoud/Desktop/projects/volleyball_analytics/runs/yolo_package/receive'
    os.makedirs(output_path, exist_ok=True)
    yolo_fmt = YoloDataset(list(action_cfg['labels'].values()))

    pbar = tqdm(images)
    count = 0
    for img_path in images:
        img_annot = yolo_fmt.create_img(img_path)
        img = cv2.imread(img_path.as_posix())
        bboxes = action_detector.detect_all(img)
        balls: List[BoundingBox] = ball_detector.detect_all(img)
        bboxes = [box for box in bboxes if box.name != 'ball']
        bboxes.extend(balls)
        if len(bboxes):
            yolo_fmt.add_bboxes(img_annot=img_annot, yolo_bboxes=bboxes)
            count += 1
        pbar.update(1)
        pbar.set_description(f"positives: {count}/{len(images)}")
    yolo_fmt.output(output_path)


