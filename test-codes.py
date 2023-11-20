import cv2
from tqdm import tqdm
from time import time
from pathlib import Path
from argparse import ArgumentParser
from src.ml.ball_detection.yolo_ball_detector import YoloBallDetector
from src.ml.action_detection.yolo_action_detector import YoloActionDetector
from src.ml.keypoint_detection.yolo_pose_estimator import YoloPoseEstimator


def config():
    parser = ArgumentParser()
    parser.add_argument(
        '--video', type=str, default='./data/raw/videos/test/videos/11_short.mp4'
    )
    parser.add_argument(
        '--output', type=str, default='./runs/inference/'
    )
    parser.add_argument("--use-pose", type=bool, default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = config()
    video_path = args.video
    output_path = args.output

    ball_detector = YoloBallDetector()
    action_detector = YoloActionDetector()
    if args.use_pose:
        kp_detector = YoloPoseEstimator()
    else:
        kp_detector = None

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), 'file does not exist...'

    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]

    filename = Path(args.output_path) / (Path(video_path).stem + '.mp4')
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    output = cv2.VideoWriter(
        filename.as_posix(),
        codec,
        fps,
        (w, h)
    )

    pbar = tqdm(list(range(7000)))

    for fno in range(7000):
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        t1 = time()
        balls = ball_detector.detect(frame)
        actions = action_detector.detect(frame)
        if args.use_pose:
            poses = kp_detector.detect(frame)
        t2 = time()
        pbar.set_description(f"processed in {t2 - t1: .4f} seconds.")

        frame = ball_detector.draw(frame, balls)
        frame = action_detector.draw(frame, actions)
        if args.use_pose:
            frame = kp_detector.draw(frame, poses)
        output.write(frame)
