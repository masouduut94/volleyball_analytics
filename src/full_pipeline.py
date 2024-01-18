from pathlib import Path

import cv2
import yaml
from tqdm import tqdm
from api.models import Match
from src.ml.video_mae.game_state.utils import Manager


def main():
    match_id = 1
    ml_config = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    setup_config = "/home/masoud/Desktop/projects/volleyball_analytics/conf/setup.yaml"
    cfg: dict = yaml.load(open(ml_config), Loader=yaml.SafeLoader)
    temp: dict = yaml.load(open(setup_config), Loader=yaml.SafeLoader)
    cfg.update(temp)

    match = Match.get(match_id)
    src = match.get_main_video()
    series_id = match.get_series().id
    video_path = src.path
    video_name = Path(video_path).name

    # state_detector = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])
    # object_detector = VolleyBallObjectDetector(config=cfg, court_keypoints_json=court_json, video_name=video_name,
    #                                            use_player_detection=True)
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "file is not accessible..."
    n_frames = int(cap.get(7))
    pbar = tqdm(list(range(n_frames)))
    state_manager = Manager(cfg=cfg, series_id=series_id, cap=cap, buffer_size=30, video_name=video_name)

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
                            vb_objects = state_manager.predict_objects(all_frames)
                            print(f'{rally_name} saved ...')
                            state_manager.rally_counter += 1
                            state_manager.reset_long_buffer()
                        elif prev_prev == 'no-play':
                            state_manager.reset_long_buffer()
                    state_manager.reset_temp_buffer()
        else:
            continue


if __name__ == '__main__':
    main()
