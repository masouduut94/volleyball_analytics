# from abc import ABC
from typing import List

# import numpy as np
from numpy.typing import NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, Meta, CourtCoordinates
from pathlib import Path
import cv2
from tqdm import tqdm

# weights = 'yolov8n.pt'

__all__ = ['PlayerDetector']


class PlayerDetector:
    def __init__(self, cfg, court_dict: dict = None):
        self.name = 'player'
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']
        self.court = None
        self.court = CourtCoordinates(court_dict) if court_dict is not None else None

    def predict(self, inputs: NDArray) -> list[BoundingBox]:
        results = self.model(inputs, classes=0)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().tolist()

        detections: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name=self.name, conf=float(conf))
            detections.append(b)
        detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return detections

    def batch_predict(self, inputs: List[NDArray]) -> List[List[BoundingBox]]:
        outputs = self.model(inputs, verbose=False, classes=0)
        results = []
        for res in outputs:
            confs = res.boxes.conf.cpu().detach().numpy().tolist()
            boxes = res.boxes.xyxy.cpu().detach().numpy().tolist()

            detections: List[BoundingBox] = []
            for box, conf in zip(boxes, confs):
                # TODO: make it suitable for multi-class yolo.
                b = BoundingBox(box, name='ball', conf=float(conf))
                detections.append(b)
            detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
            results.append(detections)
        return results

    def filter(self, bboxes: List[BoundingBox], keep: int = None, by_bbox_size: bool = True,
               by_zone: bool = True):
        """
        filter the bounding boxes of people based on the size of bounding box,
        whether their steps are in the court.
        Args:
            by_zone:
            bboxes:
            keep:
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
    def draw(frame: NDArray, bboxes: List[BoundingBox], use_marker=False, use_ellipse: bool = True,
             use_bbox: bool = True, color: tuple = Meta.green, use_title: bool = True):
        for bb in bboxes:
            if use_marker:
                frame = bb.draw_marker(frame, color)
            if use_ellipse:
                frame = bb.draw_ellipse(frame, color)
            if use_bbox:
                frame = bb.plot(frame, color, title=bb.name if use_title else '')
        return frame


if __name__ == '__main__':
    video = 'data/raw/videos/train/11.mp4'
    output = 'runs/detect/onnx'
    cfg = {
        'weight': '/home/masoud/Desktop/projects/yolov8-tensorrt-test/weights/yolov8s.onnx',
        "labels": {0: 'person'}
    }

    player_detector = PlayerDetector(cfg=cfg)
    cap = cv2.VideoCapture(video)
    assert cap.isOpened()

    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_file = Path(video) / (Path(video).stem + 'person_onnx_output.mp4')
    writer = cv2.VideoWriter(output_file.as_posix(), fourcc, fps, (w, h))
    lst = []
    for fno in tqdm(list(range(n_frames))):
        cap.set(1, fno)
        status, frame = cap.read()
        frame = cv2.resize(frame, (640, 640))
        bboxes = player_detector.predict(lst)
        frame = player_detector.draw(frame, bboxes)
        writer.write(frame)

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f'saved results in {output_file}')
