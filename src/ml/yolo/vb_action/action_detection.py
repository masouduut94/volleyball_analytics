from typing import List

import numpy as np
from numpy.typing import ArrayLike, NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, Meta, KeyPointBox

# weights = "/home/masoud/Desktop/projects/volleyball_analytics/weights/vb_actions_6_class/weights/best.pt"


class ActionDetector:
    def __init__(self, cfg):
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']

    def detect_all(self, frame: NDArray) -> List[BoundingBox]:
        results = self.model(frame, verbose=False, classes=list(self.labels.keys()))
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()
        classes = results[0].boxes.cls.cpu().detach().numpy().astype(int).tolist()
        # names = results[0].names
        detections = []

        for box, conf, cl in zip(boxes, confs, classes):
            name = self.labels[cl]
            b = BoundingBox(box, name=name, conf=float(conf))
            detections.append(b)
        return detections

    @staticmethod
    def draw(frame: NDArray, items: List[BoundingBox | KeyPointBox]):
        for bb in items:
            match bb.name:
                case 'spike':
                    frame = bb.plot(frame, color=Meta.orange, title=bb.name)
                case 'set':
                    frame = bb.plot(frame, color=Meta.yellow, title=bb.name)
                case 'receive':
                    frame = bb.plot(frame, color=Meta.green, title=bb.name)
                case 'block':
                    frame = bb.plot(frame, color=Meta.purple, title=bb.name)
        return frame
