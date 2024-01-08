import cv2
from tqdm import tqdm
from time import time
from pathlib import Path
from argparse import ArgumentParser

from src.ml.yolo.players.segmentation import PlayerSegmentor
from src.utilities.utils import CourtCoordinates
from src.ml.yolo.ball.ball_detection import BallSegmentor
from src.ml.yolo.players.detection import PlayerDetector
from src.ml.yolo.vb_action.action_detection import ActionDetector
# from src.ml.yolo.keypoint.pose_estimation import PoseEstimator

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

    ball_detector = BallSegmentor()
    action_detector = ActionDetector()
    player_detector = PlayerDetector()

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

    pbar = tqdm(list(range(7000)))

    for fno in range(7000):
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        t1 = time()
        ball = ball_detector.detect_one(frame)
        actions = action_detector.detect(frame)
        players = player_detector.detect_all(frame)
        players = player_detector.filter(players, by_bbox_size=True, by_zone=True)

        if ball is not None:
            frame = ball_detector.draw(frame, [ball])
        frame = action_detector.draw(frame, actions)
        frame = player_detector.draw(frame, players, use_marker=True, use_bbox=False)
        if fno > 1000:
            break
        output.write(frame)
        t2 = time()
        pbar.set_description(f"{t2 - t1: .4f} seconds. {fno}/{total_frames}")

    cap.release()
    output.release()
    cv2.destroyAllWindows()

    print(f'video output saved in {filename.as_posix()}')
