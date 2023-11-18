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
        confs = results[0].boxes.conf
        boxes = results[0].boxes.xyxy
        kps = results[0].keypoints.xy
        keypoints = []
        for kp, box, conf in zip(kps, boxes, confs):
            bbox = BoundingBox(box, name='ball', conf=float(conf))
            kp = KeyPointBox(keypoints=kp.cpu().detach().numpy(), bbox=bbox, name="person")
            keypoints.append(kp)

        return keypoints

