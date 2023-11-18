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
        boxes = results[0].boxes.xyxy.cpu().detach().numpy().astype(int).tolist()
        kps = results[0].keypoints.xy.cpu().detach().numpy().astype(int)
        keypoints = []
        for kp, box, conf in zip(kps, boxes, confs):
            bbox = BoundingBox(box, name='ball', conf=float(conf))
            kp = KeyPointBox(keypoints=kp, bbox=bbox, name="person")
            keypoints.append(kp)
        return keypoints

    @staticmethod
    def draw(frame: NDArray, kps: List[KeyPointBox]):
        for kp in kps:
            frame = kp.plot(frame, align_numbers=False)
        return frame
