from abc import ABC, abstractmethod
from typing import List

from numpy.typing import NDArray

from src.utilities.utils import BoundingBox, KeyPointBox, Meta


class YoloDetector(ABC):

    @abstractmethod
    def detect_all(self, frame: NDArray):
        pass

    @staticmethod
    def draw(frame: NDArray, items: List[BoundingBox | KeyPointBox], use_title: bool = False,
             use_marker: bool = False, use_bbox: bool = True, use_ellipse: bool = False,
             color: tuple = Meta.green) -> NDArray:
        for bb in items:
            if use_marker:
                frame = bb.draw_marker(frame, color)
            if use_ellipse:
                frame = bb.draw_ellipse(frame, color)
            if use_bbox:
                frame = bb.plot(frame, color=color, title=bb.name if use_title else '')
        return frame
