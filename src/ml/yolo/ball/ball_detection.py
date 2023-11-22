from typing import List
from ultralytics import YOLO
from numpy.typing import NDArray
from src.utilities.utils import BoundingBox, Meta
# weights = '/home/masoud/Desktop/projects/volleyball_analytics/weights/ball_segment/model2/weights/best.pt'

__all__ = ['BallDetector']


class BallDetector:
    def __init__(self, cfg: dict):
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']

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

    @staticmethod
    def draw(frame: NDArray, bboxes: List[BoundingBox], use_ellipse: bool = False, use_marker=False, color=Meta.green,
             use_bbox=True, use_title: bool = True):
        for bb in bboxes:
            if use_marker:
                frame = bb.draw_marker(frame, color)
            if use_ellipse:
                frame = bb.draw_ellipse(frame, color)
            if use_bbox:
                frame = bb.plot(frame, color, title=bb.name if use_title else '')
        return frame
