from abc import ABC, abstractmethod
from typing import List

from numpy.typing import NDArray

from src.utilities.utils import BoundingBox, KeyPointBox, Meta


class YoloDetector(ABC):

    @abstractmethod
    def detect_all(self, frame: NDArray):
        pass

    @staticmethod
    def draw(frame: NDArray, items: List[BoundingBox | KeyPointBox], title=None,
             use_marker=False, use_bbox=True, use_ellipse=False, color=Meta.green):
        for bb in items:
            if use_marker:
                frame = bb.draw_marker(frame, color)
            if use_ellipse:
                frame = bb.draw_ellipse(frame, color)
            if use_bbox:
                if title is not None:
                    frame = bb.plot(frame, color=color, title=title)
                else:
                    frame = bb.plot(frame, color=color)
        return frame