from typing import List

import numpy as np
from numpy.typing import NDArray
import cv2
from pathlib import Path
from tqdm import tqdm
from ultralytics import YOLO
from src.utilities.utils import BoundingBox, Meta


# weights = 'yolov8n-seg.pt'
# __all__ = ['CourtSegmentor']


class CourtSegmentor:
    def __init__(self, cfg):
        self.name = 'court'
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']

    def predict(self, frame: NDArray) -> list:
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
    def draw(frame: NDArray, points: list, color=Meta.green):
        if len(points):
            points = np.array(points)
            # frame = cv2.drawContours(frame, contours, contourIdx=-1, color=color, thickness=5)
            frame = cv2.fillPoly(frame, [points], color)
        return frame


if __name__ == '__main__':
    video = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/9.webm'
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
        frame = court_segmentor.draw(frame, points)
        writer.write(frame)
        if fno > 200:
            break

    cap.release()
    writer.release()
    print(f'saved results in {output_file}')
