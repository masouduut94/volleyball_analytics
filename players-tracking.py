from typing import List

import cv2
import numpy as np
from tqdm import tqdm
from time import time
from pathlib import Path
import norfair
from norfair import Detection, Tracker, OptimizedKalmanFilterFactory
from argparse import ArgumentParser
from src.ml.yolo.ball.ball_detection import BallDetector
from src.ml.yolo.vb_action.action_detection import ActionDetector
from src.ml.yolo.players.pose_estimation import PoseEstimator
from src.utilities.utils import BoundingBox, KeyPointBox, Meta, CourtCoordinates

DISTANCE_THRESHOLD_BBOX: float = 0.7
DISTANCE_THRESHOLD_CENTROID: int = 30
MAX_DISTANCE: int = 10000

court_coordinates = {
    "main_zone": [
        [410, 620],
        [1500, 620],
        [1830, 1040],
        [80, 1040]
    ],
    "front_zone": [
        [170, 715],
        [1750, 715],
        [1850, 850],
        [80, 850]
    ]
}

COURT = CourtCoordinates(points=court_coordinates)


def embedding_distance(matched_not_init_trackers, unmatched_trackers):
    snd_embedding = unmatched_trackers.last_detection.embedding

    if snd_embedding is None:
        for detection in reversed(unmatched_trackers.past_detections):
            if detection.embedding is not None:
                snd_embedding = detection.embedding
                break
        else:
            return 1

    for detection_fst in matched_not_init_trackers.past_detections:
        if detection_fst.embedding is None:
            continue

        distance = 1 - cv2.compareHist(
            snd_embedding, detection_fst.embedding, cv2.HISTCMP_CORREL
        )
        if distance < 0.5:
            return distance
    return 1


def convert_to_norfair_detection(
        yolo_detections: List[BoundingBox | KeyPointBox], track_points: str = "centroid") -> List[Detection]:
    """convert detections_as_xywh to norfair detections"""
    norfair_detections: List[Detection] = []

    if track_points == "centroid":
        for detection in yolo_detections:
            bbox = detection if isinstance(detection, BoundingBox) else detection.get_bbox()
            if not bbox.detected:
                continue
            centroid = np.array(
                [bbox.center[0], bbox.center[1]]
            )
            score = np.array([bbox.conf])
            norfair_detections.append(
                Detection(
                    points=centroid,
                    scores=score,
                    label=bbox.name,
                )
            )
    elif track_points == "bbox":
        for detection in yolo_detections:
            bbox = detection if isinstance(detection, BoundingBox) else detection.get_bbox()
            if not bbox.detected:
                continue
            box = np.array(
                [
                    [bbox.x1, bbox.y1],
                    [bbox.x2, bbox.y2],
                ]
            )
            scores = np.array(
                [bbox.conf, bbox.conf]
            )
            norfair_detections.append(
                Detection(
                    points=box, scores=scores, label=detection.name)
            )
    return norfair_detections


def config():
    parser = ArgumentParser()
    parser.add_argument(
        '--video', type=str, default='./data/raw/videos/test/videos/11_short.mp4'
    )
    parser.add_argument(
        '--output', type=str, default='./runs/inference/'
    )
    parser.add_argument("--use-pose", type=bool, default=False)
    parser.add_argument('--disable-reid', type=bool, default=False)
    parser.add_argument('--track-points', type=str, default='bbox')

    return parser.parse_args()


if __name__ == '__main__':
    args = config()
    video_path = args.video
    output_path = args.output
    disable_reid = args.disable_reid
    if disable_reid:
        tracker = Tracker(
            initialization_delay=1,
            distance_function="euclidean",
            hit_counter_max=10,
            filter_factory=OptimizedKalmanFilterFactory(),
            distance_threshold=50,
            past_detections_length=5,
        )
    else:
        tracker = Tracker(
            initialization_delay=1,
            distance_function="euclidean",
            hit_counter_max=10,
            filter_factory=OptimizedKalmanFilterFactory(),
            distance_threshold=50,
            past_detections_length=5,
            reid_distance_function=embedding_distance,
            reid_distance_threshold=0.5,
            reid_hit_counter_max=500,
        )

    ball_detector = BallDetector()
    action_detector = ActionDetector()
    kp_detector = PoseEstimator()

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), 'file does not exist...'

    w, h, fps, _, total_frames = [int(cap.get(i)) for i in range(3, 8)]

    filename = Path(output_path) / (Path(video_path).stem + '.mp4')
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    output = cv2.VideoWriter(
        filename.as_posix(),
        codec,
        fps,
        (w, h)
    )

    pbar = tqdm(list(range(total_frames)))

    distance_function = "iou" if args.track_points == "bbox" else "euclidean"

    distance_threshold = (
        DISTANCE_THRESHOLD_BBOX
        if args.track_points == "bbox"
        else DISTANCE_THRESHOLD_CENTROID
    )

    # tracker = Tracker(
    #     distance_function=distance_function,
    #     distance_threshold=distance_threshold,
    # )

    print("Total frames: ", total_frames)
    for fno in range(0, total_frames):
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        t1 = time()
        cv2.putText(frame, f"FNO# {fno}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, Meta.white, 2)
        ball = ball_detector.detect_one(frame)
        actions = action_detector.detect(frame)
        poses = kp_detector.detect(frame)
        t2 = time()
        pbar.set_description(f"{t2 - t1: .4f} seconds. {fno}/{total_frames}")

        player_detections = convert_to_norfair_detection(poses, track_points=args.track_points)
        tracked_players = tracker.update(detections=player_detections)
        if ball is not None:
            frame = ball_detector.draw(frame, [ball])
        frame = action_detector.draw(frame, actions)
        # if args.track_points == "centroid":
        #     norfair.draw_points(frame, player_detections)
        #     norfair.draw_tracked_objects(frame, tracked_players)
        # elif args.track_points == "bbox":
        # norfair.draw_boxes(frame, player_detections)
        norfair.draw_boxes(frame, tracked_players)
        output.write(frame)

    print(f'video output saved in {filename.as_posix()}')
