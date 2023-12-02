import os
import cv2
from tqdm import tqdm
from typing import List
from pathlib import Path
from copy import deepcopy
from natsort import natsorted
import xml.etree.ElementTree as ET
from src.utilities.utils import BoundingBox
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


if __name__ == '__main__':
    cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/vb_actions_6_class/model1/weights/best.pt',
        "labels": {
            # 0: 'ball',
            1: 'block',
            2: 'receive',
            3: 'set',
            4: 'spike',
            5: 'serve'
        }
    }
    detector = ActionDetector(cfg)

    image_dir = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/4_classes/serve'
    images = natsorted(list(Path(image_dir).glob('*.png')))
    meta_file = '/home/masoud/Desktop/projects/volleyball_analytics/notebooks/meta.xml'
    output_path = '/home/masoud/Desktop/projects/volleyball_analytics/runs'
    os.makedirs(output_path, exist_ok=True)
    cvat_fmt = CVATDataset(meta_file)
    parent = Path(image_dir).stem

    pbar = tqdm(images)
    count = 0
    for img_path in images:
        img = cv2.imread(img_path.as_posix())
        h, w, _ = img.shape
        bboxes = detector.detect_all(img)
        img_tag = cvat_fmt.create_img(img_path.name, width=w, height=h)
        if len(bboxes):
            cvat_fmt.add_bboxes(img_tag=img_tag, yolo_bboxes=bboxes)
            count += 1
        pbar.update(1)
        pbar.set_description(f"positives: {count}/{len(images)}")
    cvat_fmt.output(f'{output_path}/{parent}.xml')

