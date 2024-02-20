from typing import List
from numpy.typing import NDArray
from ultralytics import YOLO

from src.utilities.utils import KeyPointBox, Meta

# weights = 'yolov8n-pose.pt'
__all__ = ['PoseEstimator']


class PoseEstimator:
    def __init__(self, cfg: dict):
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']

    def predict(self, inputs: NDArray) -> List[KeyPointBox]:
        results = self.model(inputs, verbose=False)
        confs = results[0].boxes.conf.cpu().detach().numpy().tolist()
        kps = results[0].keypoints.xy.cpu().detach().numpy().astype(int)
        keypoints = []
        for kp, conf in zip(kps, confs):
            kp = KeyPointBox(keypoints=kp, conf=conf, name="player")
            keypoints.append(kp)
        return keypoints

    def batch_predict(self, inputs: List[NDArray]) -> List[List[KeyPointBox]]:
        outputs = self.model(inputs, verbose=False)
        results = []
        for res in outputs:
            confs = res.boxes.conf.cpu().detach().numpy().tolist()
            kps = res.keypoints.xy.cpu().detach().numpy().astype(int)

            keypoints: List[KeyPointBox] = []
            for kp, conf in zip(kps, confs):
                kp = KeyPointBox(keypoints=kp, conf=conf, name="player")
                keypoints.append(kp)
            results.append(keypoints)
        return results

    @staticmethod
    def draw(frame: NDArray, kps: List[KeyPointBox], use_marker=False, color=Meta.orange):
        for kp in kps:
            if use_marker:
                frame = kp.draw_marker(frame, color=color)
            else:
                frame = kp.draw_ellipse(frame, color=color)
        return frame
