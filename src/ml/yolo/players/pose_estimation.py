from typing import List
from numpy.typing import NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, KeyPointBox, Meta

weights = 'yolov8n-pose.pt'


class PoseEstimator:
    def __init__(self):
        self.model = YOLO(weights)

    def detect(self, frame: NDArray) -> List[KeyPointBox]:
        results = self.model(frame, verbose=False)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        kps = results[0].keypoints.xy.cpu().detach().numpy().astype(int)
        keypoints = []
        for kp, conf in zip(kps, confs):
            kp = KeyPointBox(keypoints=kp, conf=conf, name="player")
            keypoints.append(kp)
        return keypoints

    @staticmethod
    def draw(frame: NDArray, kps: List[KeyPointBox], use_marker=False, color=Meta.orange):
        for kp in kps:
            if use_marker:
                frame = kp.draw_marker(frame, color=color)
            else:
                frame = kp.draw_ellipse(frame, color=color)
        return frame
