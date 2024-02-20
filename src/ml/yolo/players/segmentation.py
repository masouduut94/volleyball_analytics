from typing import List
from ultralytics import YOLO
from numpy.typing import NDArray

from src.utilities.utils import BoundingBox, Meta, CourtCoordinates

# weights = 'yolov8n-seg.pt'
__all__ = ['PlayerSegmentor']


class PlayerSegmentor:
    def __init__(self, cfg, court_dict: dict = None):
        self.name = 'player'
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']
        self.court = CourtCoordinates(court_dict) if court_dict is not None else None

    def predict(self, frame: NDArray) -> list[BoundingBox]:
        results = self.model(frame, verbose=False, classes=0)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        detections: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name=self.name, conf=float(conf))
            detections.append(b)
        detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return detections

    def batch_predict(self, frame: List[NDArray]) -> list[List[BoundingBox]]:
        outputs = self.model(frame, verbose=False, classes=0)
        results = []
        for output in outputs:
            confs = output.boxes.conf.cpu().detach().numpy().tolist()
            boxes = output.boxes.xyxy.cpu().detach().numpy().tolist()

            detections: List[BoundingBox] = []
            for box, conf in zip(boxes, confs):
                b = BoundingBox(box, name=self.name, conf=float(conf))
                detections.append(b)
            detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
            results.append(detections)
        return results

    def filter(self, bboxes: List[BoundingBox], keep: int = None, by_bbox_size: bool = True, by_zone: bool = True):
        """
        filter the bounding boxes of people based on the size of bounding box,
        and also whether their steps are in the court or not.
        Args:
            by_zone:
            bboxes:
            keep: how many people to keep. normally 12 person. (6 for one team, 6 for other team)
            by_bbox_size:

        Returns:

        """
        if self.court is not None:
            # Keep the players that their legs keypoint (x, y) are inside the polygon-shaped court ...
            if by_zone:
                bboxes = [b for b in bboxes if
                          any([self.court.is_inside_main_zone(b.left_down),
                               self.court.is_inside_main_zone(b.right_down),
                               self.court.is_inside_main_zone(b.center),
                               self.court.is_inside_front_zone(b.left_down),
                               self.court.is_inside_front_zone(b.right_down)])]
        if by_bbox_size:
            bboxes.sort(key=lambda x: (x.conf, x.area))
        else:
            bboxes.sort(key=lambda x: x.conf)
        # https://stackoverflow.com/questions/14161331/creating-your-own-contour-in-opencv-using-python
        return bboxes[:keep] if keep is not None else bboxes

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
