from typing import List

import numpy as np
import yaml
import json
from os.path import isfile
from numpy.typing import NDArray
from yaml.loader import SafeLoader

from src.utilities.utils import BoundingBox
from .ball import BallSegmentor
from .vb_action import ActionDetector
from .players import PlayerSegmentor, PlayerDetector, PoseEstimator


class VolleyBallObjectDetector:
    def __init__(self, ml_yaml, court_keypoints_json: str = None, video_name: str = None, use_player_detection=True):
        self.config = self._parse_configs(ml_yaml)
        court_dict = None
        if court_keypoints_json is not None and video_name is not None:
            court_dict = json.load(open(court_keypoints_json))[video_name]
            # TODO: create a model to segment the court at first sight, or make us capable of annotating the court
            #       keypoints on a GUI ...
        if use_player_detection:
            self.player_detector = PlayerDetector(self.config['yolo']['player_detection'], court_dict=court_dict)
        else:
            self.player_detector = PlayerSegmentor(self.config['yolo']['player_segmentation'], court_dict=court_dict)
        self.action_detector = ActionDetector(self.config['yolo']['action_detection6'])
        self.ball_detector = BallSegmentor(self.config['yolo']['ball_segmentation'])
        self.pose_estimator = PoseEstimator(self.config['yolo']['pose_estimation'])

    @staticmethod
    def _parse_configs(ml_yaml):
        assert isfile(ml_yaml)
        with open(ml_yaml) as cfg_file:
            cfg = yaml.load(cfg_file, Loader=SafeLoader)
        return cfg

    # TODO: FIXME: Make code adaptable to batch processing ...
    def detect_balls(self, inputs: NDArray | List[NDArray]):
        if isinstance(inputs, np.ndarray):
            return self.ball_detector.predict(inputs=inputs)
        else:
            return self.ball_detector.batch_predict(inputs=inputs)

    def detect_actions(self, inputs: NDArray | List[NDArray], exclude=None):
        if isinstance(inputs, np.ndarray):
            return self.action_detector.predict(inputs=inputs, exclude=exclude)
        else:
            return self.action_detector.batch_predict(inputs=inputs, exclude=exclude)

    def detect_keypoints(self, inputs: NDArray | List[NDArray]):
        if isinstance(inputs, np.ndarray):
            return self.pose_estimator.predict(inputs=inputs)
        else:
            return self.pose_estimator.batch_predict(inputs=inputs)

    def segment_players(self, inputs: NDArray | List[NDArray]):
        return self.player_detector.predict(frame=inputs)

    def extract_objects(self, bboxes: List[BoundingBox], item: str = 'ball'):
        return self.action_detector.extract_classes(bboxes=bboxes, item=item)

    def draw_bboxes(self, image, bboxes):
        image = self.action_detector.draw(frame=image, items=bboxes)
        return image


if __name__ == '__main__':
    config_file = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    court_json = '/home/masoud/Desktop/projects/volleyball_analytics/conf/court.json'
    vb_detector = VolleyBallObjectDetector(config_file, court_json)
