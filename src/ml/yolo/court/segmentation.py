import math
from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray
import cv2
from pathlib import Path
from tqdm import tqdm
from ultralytics import YOLO
from src.utilities.utils import Meta


# weights = 'yolov8n-seg.pt'
# __all__ = ['CourtSegmentor']


class CourtSegmentor:
    def __init__(self, cfg):
        self.name = 'court'
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']

    def predict(self, frame: NDArray) -> List[List[int]]:
        results = self.model(frame, verbose=False, classes=0)
        points = []
        if results[0].masks is not None:
            for array in results[0].masks.xy:
                array = array.astype(int)
                for item in array:
                    item = item.tolist()
                    points.append(item)
        return points

    @staticmethod
    def find_corners(frame: NDArray, mask_points: List[List[int]]) -> Tuple:
        h, w, _ = frame.shape
        top_left_corner = (0, 0)
        top_right_corner = (w, 0)
        down_left_corner = (0, h)
        down_right_corner = (w, h)

        down_left = None
        down_right = None
        top_left = None
        top_right = None

        if len(mask_points):
            points = sorted(mask_points, key=lambda x: math.dist(x, down_left_corner))
            down_left = points[0]
            points = sorted(mask_points, key=lambda x: math.dist(x, down_right_corner))
            down_right = points[0]
            points = sorted(mask_points, key=lambda x: math.dist(x, top_left_corner))
            top_left = points[0]
            points = sorted(mask_points, key=lambda x: math.dist(x, top_right_corner))
            top_right = points[0]
        return top_left, down_left, down_right, top_right

    @staticmethod
    def draw(frame: NDArray, points: list, color=Meta.green):
        if len(points):
            points = np.array(points)
            frame = cv2.fillPoly(frame, [points], color)
        return frame


if __name__ == '__main__':
    video = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/3.mp4'
    output = '/home/masoud/Desktop/projects/volleyball_analytics/runs/DEMO'
    cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/court_segment/weights/best.pt',
        "labels": {0: 'court'}
    }

    court_segmentor = CourtSegmentor(cfg=cfg)
    cap = cv2.VideoCapture(video)
    assert cap.isOpened()

    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_file = Path(output) / (Path(video).stem + '___COURT_VISUAL.mp4')
    writer = cv2.VideoWriter(output_file.as_posix(), fourcc, fps, (w, h))

    for fno in tqdm(list(range(n_frames))):
        cap.set(1, fno)
        status, frame = cap.read()
        points = court_segmentor.predict(frame)
        top_left = (0, 0)
        top_right = (w, 0)
        down_left = (0, h)
        down_right = (w, h)
        # frame = court_segmentor.draw(frame, points)
        if len(points):
            tl, dl, dr, tr = court_segmentor.find_corners(frame, points)
            cv2.circle(frame, tuple(tl), 10, (255, 0, 0), 3)
            cv2.circle(frame, tuple(dl), 10, (0, 255, 0), 3)
            cv2.circle(frame, tuple(dr), 10, (0, 0, 255), 3)
            cv2.circle(frame, tuple(tr), 10, (255, 0, 255), 3)

        writer.write(frame)
        if fno > 100:
            break

    cap.release()
    writer.release()
    print(f'saved results in {output_file}')
