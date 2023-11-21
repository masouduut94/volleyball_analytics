from typing import List

import numpy as np
from numpy.typing import ArrayLike, NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, Meta

weights = '/home/masoud/Desktop/projects/volleyball_analytics/runs/segment/train/weights/best.pt'


class BallDetector:
    def __init__(self):
        self.model = YOLO(weights)

    def detect(self, frame: NDArray) -> BoundingBox | None:
        results = self.model(frame, verbose=False, imgsz=640)
        confs: List[float] = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes: List[list] = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        dets: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name='ball', conf=float(conf))
            dets.append(b)

        dets.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return dets[0] if len(dets) else None

    def detect_all(self, frame: NDArray) -> list[BoundingBox]:
        results = self.model(frame, verbose=False)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        dets: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name='ball', conf=float(conf))
            dets.append(b)
        dets.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return dets

    def draw(self, frame: NDArray, bboxes: List[BoundingBox]):
        for bb in bboxes:
            frame = bb.plot(frame, Meta.red, title=f'ball {bb.conf: .2f}')
        return frame
