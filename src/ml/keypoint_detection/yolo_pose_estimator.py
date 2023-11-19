from typing import List
from numpy.typing import NDArray
from ultralytics import YOLO

from src.utilities.utils import BoundingBox, KeyPointBox

weights = 'yolov8n-pose.pt'


class YoloPoseEstimator:
    def __init__(self):
        self.model = YOLO(weights)

    def detect(self, frame: NDArray) -> List[KeyPointBox]:
        results = self.model(frame, verbose=False)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        kps = results[0].keypoints.xy.cpu().detach().numpy().astype(int)
        keypoints = []
        for kp, conf in zip(kps, confs):
            kp = KeyPointBox(keypoints=kp, conf=conf, name="person")
            keypoints.append(kp)
        return keypoints

    @staticmethod
    def draw(frame: NDArray, kps: List[KeyPointBox]):
        for kp in kps:
            frame = kp.plot(frame, align_numbers=False)
        return frame
