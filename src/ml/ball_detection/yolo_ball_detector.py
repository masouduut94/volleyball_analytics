from typing import List

import numpy as np
from numpy.typing import ArrayLike, NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, Meta

weights = '/home/masoud/Desktop/projects/volleyball_analytics/src/yolov8/runs/segment/train/weights/best.pt'


class YoloBallDetector:
    def __init__(self):
        self.model = YOLO(weights)

    def detect(self, frame: NDArray) -> List[BoundingBox]:
        results = self.model(frame, verbose=False)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        dets = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class detection.
            b = BoundingBox(box, name='ball', conf=float(conf))
            dets.append(b)
        return dets

    def draw(self, frame: NDArray, bboxes: List[BoundingBox]):
        for bb in bboxes:
            frame = bb.plot(frame, Meta.red, title='ball')
        return frame
