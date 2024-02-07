from argparse import ArgumentParser
from typing import List

import cv2
from natsort import natsorted
from tqdm import tqdm

from api.data_classes import RallyData
from api.models import Rally, Video, Match
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector

"""
Custom serialization for sqlalchemy objects

https://variable-scope.com/posts/creating-a-json-column-type-for-sqlalchemy

make sets, blocks, ....  a list of bounding boxes when returning. 
Also you can develop the FastAPI and get help from them to get items.
"""

# def parse_args():
#     parser = ArgumentParser()
#     parser.add_argument(
#         '--match-id',
#     )

if __name__ == '__main__':
    match_id = 1
    match: Match = Match.get(match_id)
    video: Video = match.new_video()
    rallies: List[Rally] = match.get_rallies()
    # TODO: Check if you can add asyncIO
    for rally in tqdm(rallies):
        cap = cv2.VideoCapture(rally.new_video.path)
        # rally_data = RallyData.from_instance(rally)
        w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

        bk = rally.blocks
        st = rally.sets
        sp = rally.spikes
        bl = rally.ball_positions
        sv = rally.service
        rv = rally.receives

        frame_numbers = set(
            list(bk.keys()) + list(st.keys()) + list(sp.keys()) + list(bl.keys()) + list(sv.keys()) + list(rv.keys())
        )

        for fno in frame_numbers:
            sfno = str(fno)
            bk = rally.blocks[sfno]
            bl = rally.balls[sfno]
            st = rally.sets[sfno]
            sv = rally.service[sfno]
            rv = rally.receives[sfno]

            # for block in bk:

        # Get items from rally jsons.
        # Go forward with frame -> check if there exists the frame number in jsons, and draw things on it.
        # Also draw ball like a following line on screen for 6-10 frames.
        # Draw it on frames.
