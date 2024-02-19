import os
from pathlib import Path
from typing import List, Any

import cv2
import numpy as np
from numpy.typing import ArrayLike, NDArray
from tqdm import tqdm
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, Meta, KeyPointBox


class ActionDetector:
    def __init__(self, cfg):
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']
        self.labels2ids = {v: k for k, v in self.labels.items()}

    def predict(self, inputs: NDArray, verbose=False, exclude=None) -> dict[str, List[BoundingBox]]:
        detect_ids = {k: v for k, v in self.labels2ids.items() if k != exclude}
        outputs = self.model.predict(inputs, verbose=verbose, classes=list(detect_ids.values()))

        confs = outputs[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = outputs[0].boxes.xyxy.cpu().detach().numpy().tolist()
        classes = outputs[0].boxes.cls.cpu().detach().numpy().astype(int).tolist()
        temp = {v: [] for v in self.labels.values()}
        for box, conf, cl in zip(boxes, confs, classes):
            name = self.labels[cl]
            b = BoundingBox(box, name=name, conf=float(conf))
            try:
                temp[name].append(b)
            except KeyError:
                temp[name] = [b]

        return temp

    def batch_predict(self, inputs: List[NDArray], verbose=False, exclude=None) -> List[dict[str, List[BoundingBox]]]:
        detect_ids = {k: v for k, v in self.labels2ids.items() if k != exclude}
        # TODO: Add exclude to the init function to reduce latency.
        # TODO: Split the list into a list of dictionaries for actions. by try except
        outputs = self.model.predict(inputs, verbose=verbose, classes=list(detect_ids.values()))

        results = []
        for output in outputs:
            confs = output.boxes.conf.cpu().detach().numpy().tolist()
            boxes = output.boxes.xyxy.cpu().detach().numpy().tolist()
            classes = output.boxes.cls.cpu().detach().numpy().astype(int).tolist()
            temp = {v: [] for v in self.labels.values()}
            for box, conf, cl in zip(boxes, confs, classes):
                name = self.labels[cl]
                b = BoundingBox(box, name=name, conf=float(conf))
                try:
                    temp[name].append(b)
                except KeyError:
                    temp[name] = [b]
            results.append(temp)
        return results

    @staticmethod
    def extract_classes(bboxes: List[BoundingBox], item: str) -> List[BoundingBox]:
        return [bbox for bbox in bboxes if bbox.name == item]

    @staticmethod
    def draw(frame: NDArray, items: List[BoundingBox | KeyPointBox]):
        for bb in items:
            match bb.name:
                case 'spike':
                    frame = bb.plot(frame, color=Meta.bgr_orange, title=bb.name)
                case 'set':
                    frame = bb.plot(frame, color=Meta.bgr_aqua, title=bb.name)
                case 'receive':
                    frame = bb.plot(frame, color=Meta.green, title=bb.name)
                case 'block':
                    frame = bb.plot(frame, color=Meta.bgr_purple, title=bb.name)
                case 'serve':
                    frame = bb.plot(frame, color=Meta.bgr_brown, title=bb.name)
                case 'ball':
                    frame = bb.plot(frame, color=Meta.bgr_red, title=bb.name)
        return frame


if __name__ == '__main__':
    video = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/test/videos/11_short.mp4'
    output = '/home/masoud/Desktop/projects/volleyball_analytics/runs/inference/det'
    os.makedirs(output, exist_ok=True)
    cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/vb_actions_6_class/model1/weights/best.pt',
        "labels": {0: 'spike', 1: 'block', 2: 'receive', 3: 'set'}
    }

    action_detector = ActionDetector(cfg=cfg)
    cap = cv2.VideoCapture(video)
    assert cap.isOpened()

    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_file = Path(output) / (Path(video).stem + '_output.mp4')
    writer = cv2.VideoWriter(output_file.as_posix(), fourcc, fps, (w, h))

    for fno in tqdm(list(range(n_frames))):
        cap.set(1, fno)
        status, frame = cap.read()
        bboxes = action_detector.predict(frame)
        frame = action_detector.draw(frame, bboxes)
        writer.write(frame)

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f'saved results in {output_file}')
