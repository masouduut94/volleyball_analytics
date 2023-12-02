import yaml
import json
from os.path import isfile
from numpy.typing import NDArray
from yaml.loader import SafeLoader

from ball import BallDetector
from vb_action import ActionDetector
from players import PlayerSegmentator, PlayerDetector, PoseEstimator


class VolleyBallObjectDetector:
    def __init__(self, ml_yaml, court_keypoints_json: str = None, use_player_detection=True):
        self.config = self._parse_configs(ml_yaml)
        court_dict = json.load(open(court_keypoints_json)) if court_keypoints_json is not None else None
        if use_player_detection:
            self.player_detector = PlayerDetector(self.config['yolo']['player_detection'], court_dict=court_dict)
        else:
            self.player_detector = PlayerSegmentator(self.config['yolo']['player_segmentation'])
        self.action_detector = ActionDetector(self.config['yolo']['action_detection'])
        self.ball_detector = BallDetector(self.config['yolo']['ball_detection'])
        self.pose_estimator = PoseEstimator(self.config['yolo']['pose_estimation'])

    @staticmethod
    def _parse_configs(ml_yaml):
        assert isfile(ml_yaml)
        with open(ml_yaml) as cfg_file:
            cfg = yaml.load(cfg_file, Loader=SafeLoader)
        return cfg

    def detect_ball(self, image: NDArray):
        return self.ball_detector.detect_one(frame=image)

    def detect_actions(self, image):
        return self.action_detector.detect_all(frame=image)

    def detect_players(self, image):
        return self.player_detector.detect_all(frame=image)

    def detect_keypoints(self, image):
        return self.pose_estimator.detect_all(frame=image)

    def segment_players(self, image):
        return self.player_detector.detect_all(frame=image)


if __name__ == '__main__':
    config_file = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    court_json = '/home/masoud/Desktop/projects/volleyball_analytics/conf/court.json'
    vb_detector = VolleyBallObjectDetector(config_file, court_json)
