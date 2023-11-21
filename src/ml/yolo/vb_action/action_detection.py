from typing import List

import numpy as np
from numpy.typing import ArrayLike, NDArray
from ultralytics import YOLO

from src.ml.abstract.yolo_detector import YoloDetector
from src.utilities.utils import BoundingBox, Meta, KeyPointBox

weights = "/home/masoud/Desktop/projects/volleyball_analytics/src/yolov8/runs/detect/train/weights/best.pt"


class ActionDetector(YoloDetector):
    def __init__(self):
        self.model = YOLO(weights)

    def detect_all(self, frame: NDArray) -> List[BoundingBox]:
        results = self.model(frame, verbose=False, classes=[1, 2, 3, 4])
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()
        classes = results[0].boxes.cls.cpu().detach().numpy().astype(int).tolist()
        names = results[0].names
        detections = []

        for box, conf, cl in zip(boxes, confs, classes):
            name = names[cl]
            b = BoundingBox(box, name=name, conf=float(conf))
            detections.append(b)
        return detections

    # TODO: Insert Spike-Set-Reception-Block -> to objects titles ...
    @staticmethod
    def draw(frame: NDArray, items: List[BoundingBox | KeyPointBox], use_title: str = None,
             use_marker: bool = False, use_bbox: bool = True, use_ellipse: bool = False,
             color: tuple = Meta.green):
        pass