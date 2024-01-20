from argparse import ArgumentParser
from typing import List

import cv2
from tqdm import tqdm

from api.models import Rally, Video, Match
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector


# def parse_args():
#     parser = ArgumentParser()
#     parser.add_argument(
#         '--match-id',
#     )

if __name__ == '__main__':
    match_id = 1
    match: Match = Match.get(match_id)
    video: Video = Match.get_main_video(video_id=match.video_id)
    rallies: List[Rally] = match.get_rallies()

    for rally in tqdm(rallies):
        cap = cv2.VideoCapture(rally.video.path)
        # Get items from rally jsons.
        # Go forward with frame -> check if there exists the frame number in jsons, and draw things on it.
        # Also draw ball like a following line on screen for 6-10 frames.
        # Draw it on frames.


