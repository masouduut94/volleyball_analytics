from typing import List

import numpy as np
from numpy.typing import ArrayLike, NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, Meta

weights = '/home/masoud/Desktop/projects/volleyball_analytics/runs/segment/train/weights/best.pt'


class BallDetector:
    def __init__(self):
        self.model = YOLO(weights)

    def detect_one(self, frame: NDArray) -> BoundingBox | None:
        results = self.model(frame, verbose=False, imgsz=640)
        confs: List[float] = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes: List[list] = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        detections: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name='ball', conf=float(conf))
            detections.append(b)

        detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return detections[0] if len(detections) else None

    def detect_all(self, frame: NDArray) -> list[BoundingBox]:
        results = self.model(frame, verbose=False)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        detections: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name='ball', conf=float(conf))
            detections.append(b)
        detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return detections

