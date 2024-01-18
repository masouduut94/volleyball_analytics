from pathlib import Path

import cv2
import yaml
from tqdm import tqdm
from api.models import Match
from src.ml.video_mae.game_state.utils import Manager
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector

if __name__ == '__main__':
    match_id = 1
    base_dir = "/media/masoud/HDD-8TB/DATA/volleyball/"
    config = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    cfg = yaml.load(open(config), Loader=yaml.SafeLoader)
    model = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])

    match = Match.get(match_id)
    src = match.get_main_video()
    series_id = match.get_series().id
    video_path = src.path

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "file is not accessible..."
    width, height, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    previous_state = 'no-play'
    current_state = None
    no_play_flag = 0
    state_manager = Manager(
        base_dir=base_dir, match_id=match_id, series_id=series_id,
        fps=30, width=width, height=height, buffer_size=30
    )
    pbar = tqdm(list(range(n_frames)))
    rally = None

    for fno in pbar:
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        state_manager.append_frame(frame, fno)

        if state_manager.is_full():
            current_frames, current_fnos = state_manager.get_current_frames_and_fnos()
            current_state = model.predict(current_frames)
            state_manager.set_current_state(current_state)
            pbar.set_description(f"state: {current_state}")
            current = state_manager.current
            prev = state_manager.prev
            prev_prev = state_manager.prev_prev

            match current:
                case 'service':
                    if prev in ['no-play', 'service', 'play']:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                case 'play':
                    if prev == 'service':
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames),
                                           set_serve_last_frame=True)
                    elif prev == 'play' or prev == 'no-play':
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                case 'no-play':
                    if prev == 'service' or prev == 'play':
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                    elif prev == 'no-play':
                        if prev_prev == 'play' or prev_prev == 'service':
                            all_labels = state_manager.get_labels()
                            all_frames = state_manager.get_long_buffer()
                            all_fnos = state_manager.get_long_buffer_fno()
                            start_frame = all_fnos[0]
                            rally_name = state_manager.get_path(start_frame, video_type='rally')
                            done = state_manager.write_video(rally_name, all_labels, all_frames, all_fnos,
                                                             draw_label=True)
                            service_last_frame = state_manager.service_last_frame
                            saved = state_manager.db_store(rally_name, all_fnos, service_last_frame, all_labels)
                            print(f'{rally_name} saved ...')
                            state_manager.rally_counter += 1
                            state_manager.reset_long_buffer()
                        elif prev_prev == 'no-play':
                            state_manager.reset_long_buffer()
                    state_manager.reset_temp_buffer()
        else:
            continue
