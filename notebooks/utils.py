import matplotlib.pyplot as plt
import numpy as np
from os import makedirs
from os.path import isfile, join
from pathlib import Path, PosixPath
import cv2
from shutil import copy2

from numpy.typing import ArrayLike
from typing import Any, List, Tuple


class Bbox:
    def __init__(self, xyxy: list | tuple, label: int):
        self.x1 = int(xyxy[0])
        self.y1 = int(xyxy[1])
        self.x2 = int(xyxy[2])
        self.y2 = int(xyxy[3])
        self.label = label
        # Fixme: Adapt label to COCO format in future.
        self.pt1 = (self.x1, self.y1)
        self.pt2 = (self.x2, self.y2)
        self.width = abs(self.x2 - self.x1)
        self.height = abs(self.y2 - self.y1)

    def to_yolo(self, img_width: int, img_height: int) -> List[float]:
        l = self.label
        x_cen = (self.x1 + self.width/2) / img_width
        y_cen = (self.y1 + self.height/2) / img_height
        width = (self.width / img_width)
        height = (self.height / img_height)
        
        return f"{l} {x_cen} {y_cen} {width} {height}"

    def draw(self, img: ArrayLike, color: tuple = (255, 0, 0)) -> ArrayLike:
        img = cv2.rectangle(img, self.pt1, self.pt2, color, 2)
        return img

class Segment:
    def __init__(self, polygon: List[float | int], label: int):
        self.polygon = polygon
        self.pts = self.chunk(polygon)
        self.label = label
        
    def chunk(self, arr: List) -> List[ArrayLike]:
        return [np.array(arr[i:i + 2]).reshape((-1,1,2)).astype(np.int32) for i in range(0, len(arr), 2)]

    def segment_to_yolo(self, img_w, img_h):
        text = f"{self.label} "
        for i, p in enumerate(self.polygon):
            if i % 2 == 0: # x points / img_w
                text += f" {p/img_w}"
            else: # y points / img_h
                text += f" {p/img_h}"
        return text
    
    def get_bbox(self) -> Bbox:
        Xs = [int(item) for i, item in enumerate(self.polygon) if i%2 == 0]
        Ys = [int(item) for i, item in enumerate(self.polygon) if i%2 == 1]
        x1, y1 = min(Xs), min(Ys)
        x2, y2 = max(Xs), max(Ys)
        bbox = Bbox([x1, y1, x2, y2], self.label)
        return bbox
    
    def draw(self, img: ArrayLike, color: tuple = (0, 255, 0), draw_bbox = True) -> ArrayLike:
        img = cv2.drawContours(img, self.pts, -1, color, 3)
        bbox: Bbox = self.get_bbox()
        if draw_bbox:
            img = bbox.draw(img, color=color)
        return img


class ImageAnnot:
    # Fixme: Adapt the framework for training bbox annotated project. right now it is decent for segmentation project.
    # Decouple Segment with Bbox.
    def __init__(self, img_path: str | PosixPath):
        self.img_path = Path(img_path)
        assert self.img_path.is_file()
        self.name = self.img_path.name
        self.segments = []
        self.img_w, self.img_h = self.get_img_size()
    
    def get_img_size(self):
        img = cv2.imread(self.img_path.as_posix())
        h, w, _ = img.shape
        return w, h
        
    def add_segment(self, segment: Segment) -> None:
        self.segments.append(segment)

    def get_yolo_format(self, only_bboxes=True):
        temp = ""
        for i, item in enumerate(self.segments):
            if not only_bboxes:
                segment_txt = item.segment_to_yolo(self.img_w, self.img_h)
                temp += segment_txt
            else:
                temp += item.get_bbox().to_yolo(self.img_w, self.img_h)
            if i != len(self.segments) - 1:
                temp += '\n'
        return temp

    def save_labels(self, save_path: str = "base_dir", train: bool = True, only_bboxes: bool = True):
        output = self.get_yolo_format(only_bboxes=only_bboxes)
        file_name = self.img_path.stem
        
        if train:
            img_path = join(save_path, 'images', 'train')
            label_path = join(save_path, 'labels', 'train')
        else:
            img_path = join(save_path, 'images', 'val')
            label_path = join(save_path, 'labels', 'val')

        makedirs(label_path, exist_ok=True)
        makedirs(img_path, exist_ok=True)
        
        label_path = join(label_path, file_name + '.txt')
        copy2(self.img_path.as_posix(), img_path)
        with open(label_path, 'w') as file:
            file.write(output)
        
    def get_coco_format(self):
        pass

    def img_show(self, color: tuple = (0, 255, 0)):
        img = cv2.imread(self.img_path.as_posix())
        img = cv2.cvtColor(img, 4)
        for segment in self.segments:
            img = segment.draw(img, color=color, draw_bbox=True)
        return img