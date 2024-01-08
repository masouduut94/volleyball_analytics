from pathlib import Path

import cv2
from tqdm import tqdm

from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector
from argparse import ArgumentParser


def config():
    parser = ArgumentParser("arguments for running volleyball action detection on videos...")
    parser.add_argument(

        "--model_cfg",
        type=str,
        default='/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    )
    parser.add_argument(
        '--video_path',
        type=str,
        default="/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/20.mp4"
    )
    parser.add_argument(
        '--output_path',
        type=str,
        default="/home/masoud/Desktop/projects/volleyball_analytics/runs/detect"
    )
    parser.add_argument(
        "--use_segment",
        type=bool,
        default=True
    )
    parser.add_argument(
        "--court",
        type=str,
        default="/home/masoud/Desktop/projects/volleyball_analytics/conf/court.json"
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    """
    1. Draw ball and ball tracking history in 5-6 frames before...
    2. Draw spiker-blocker-receiver-setter-Service ...
    
    """
    cfg = config()
    video_path = Path(cfg.video_path)
    output_path = Path(cfg.output_path)
    detector = VolleyBallObjectDetector(cfg.model_cfg, cfg.court, use_player_detection=cfg.use_segment,
                                        video_name=video_path.name)

    cap = cv2.VideoCapture(video_path.as_posix())
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    pbar = tqdm(total=n_frames)

    output = output_path / (video_path.stem + '_output.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(
        output.as_posix(), fourcc, fps, (w, h)
    )

    for fno in range(n_frames):
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()

        # ball = detector.detect_ball(frame)
        vb_objects = detector.detect_actions(frame)

        balls = detector.extract_actions(vb_objects, item='ball')
        blocks = detector.extract_actions(vb_objects, item='block')
        sets = detector.extract_actions(vb_objects, item='set')
        spikes = detector.extract_actions(vb_objects, item='spike')
        receives = detector.extract_actions(vb_objects, item='receive')
        services = detector.extract_actions(vb_objects, item='serve')

        frame = detector.draw_bboxes(frame, vb_objects)
        description = f"balls: {len(balls)} | blocks: {len(blocks)} | sets: {len(sets)} | spikes: {len(spikes)} | recieves: {len(receives)} | services: {len(services)}"
        pbar.set_description(description)
        writer.write(frame)

    writer.release()
    cap.release()
