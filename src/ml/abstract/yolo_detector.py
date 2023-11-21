from abc import ABC, abstractmethod
from typing import List

from numpy.typing import NDArray

from src.utilities.utils import BoundingBox, KeyPointBox, Meta


class YoloDetector(ABC):

    @abstractmethod
    def detect_all(self, frame: NDArray):
        pass

    @abstractmethod
    def detect_one(self, frame: NDArray):
        pass

    @staticmethod
    def draw(frame: NDArray, items: List[BoundingBox | KeyPointBox],
             use_marker=False, use_bbox=True, color=Meta.green):
        for bb in items:
            if use_marker:
                frame = bb.draw_marker(frame, color)
            else:
                frame = bb.draw_ellipse(frame, color)
            if use_bbox:
                frame = bb.plot(frame, color)
        return frame