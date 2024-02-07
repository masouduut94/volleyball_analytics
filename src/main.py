"""
This code gets the match and video data from db, and runs the ML processing pipeline that consists of
video classification model (HuggingFace VideoMAE) and Volleyball-Specific object detection models
(Ultralytics Yolov8) on the fetched video file.
Then the statistics and outputs are stored on the db to get ready for visualization.

"""

import cv2
import numpy as np
import yaml
from tqdm import tqdm
from pathlib import Path

from typing_extensions import List

from src.backend.app.api_interface import APIInterface
from src.backend.app.enums.enums import GameState

from src.ml.video_mae.game_state.utils import Manager


def main():
    """
    team1_id=7 team2_id=8 series_id=2 video_id=4 id=1

    Returns
    -------

    """
    match_id = 1
    ml_config = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    setup_config = "/home/masoud/Desktop/projects/volleyball_analytics/conf/setup.yaml"
    api_base_url = "http://localhost:8000"
    cfg: dict = yaml.load(open(ml_config), Loader=yaml.SafeLoader)
    temp: dict = yaml.load(open(setup_config), Loader=yaml.SafeLoader)
    cfg.update(temp)
    state_manager = Manager(cfg=cfg, buffer_size=30, url=api_base_url)
    cap = cv2.VideoCapture(state_manager.video.path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    assert cap.isOpened(), "file is not accessible..."
    n_frames = int(cap.get(7))
    pbar = tqdm(list(range(n_frames)))

    for fno in pbar:
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        state_manager.append_frame(frame, fno)

        if state_manager.is_full():
            current_frames, current_fnos = state_manager.get_current_frames_and_fnos()
            current_state = state_manager.predict_state(current_frames)
            pbar.set_description(f"state: {current_state}")
            current = state_manager.current
            prev = state_manager.prev
            prev_prev = state_manager.prev_prev

            match current:
                case GameState.SERVICE:
                    if prev in [GameState.NO_PLAY, GameState.SERVICE, GameState.PLAY]:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                case GameState.PLAY:
                    if prev == GameState.SERVICE:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                        if state_manager.service_last_frame is None:
                            state_manager.service_last_frame = len(state_manager.long_buffer_fno) - 1
                    elif prev == GameState.PLAY or prev == GameState.NO_PLAY:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                case GameState.NO_PLAY:
                    if prev == GameState.SERVICE or prev == GameState.PLAY:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                    elif prev == GameState.NO_PLAY:
                        if prev_prev == GameState.PLAY or prev_prev == GameState.SERVICE:
                            all_labels: List[int] = state_manager.get_labels()
                            all_frames: List[np.ndarray] = state_manager.get_long_buffer()
                            all_fnos: List[int] = state_manager.get_long_buffer_fno()
                            start_frame = all_fnos[0]
                            rally_name: Path = state_manager.get_path(start_frame, video_type='rally')
                            state_manager.write_video(
                                path=rally_name,
                                width=width,
                                height=height,
                                fps=fps,
                                labels=all_labels,
                                long_buffer=all_frames,
                                long_buffer_fno=all_fnos,
                                draw_label=True
                            )
                            # TODO: Try process optimization:
                            #  - parallel processing
                            #  - cython, jit
                            #  - asyncio, asyncio.Queue
                            #  - Keep the results in RabbitMQ and then create analytics from them on a async process.
                            #  - Create KPIs based on outputs.
                            #  - Select the best model from YOLO models.
                            #  - Create TEST SET for yolo model.
                            #  - Create demo for your work.
                            rally_schema = state_manager.db_store(
                                rally_name, all_fnos, state_manager.service_last_frame, all_labels
                            )
                            vb_objects = state_manager.predict_objects(all_frames)
                            done = state_manager.save_objects(rally_schema, vb_objects)
                            print(f'{rally_name} saved: {done} ...')
                            state_manager.rally_counter += 1
                            state_manager.reset_long_buffer()
                        elif prev_prev == GameState.NO_PLAY:
                            state_manager.reset_long_buffer()
                    state_manager.reset_temp_buffer()
        else:
            continue


if __name__ == '__main__':
    main()
