import cv2
import yaml
from tqdm import tqdm
from api.models import Match
from src.ml.video_mae.game_state.utils import Manager
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector

if __name__ == '__main__':
    match_id = 1
    # team1_id = 1
    # team2_id = 2
    base_dir = "/media/masoud/HDD-8TB/DATA/volleyball/"

    config = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    cfg = yaml.load(open(config), Loader=yaml.SafeLoader)
    model = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])

    match = Match.get(match_id)
    src = match.get_main_video()
    series_id = match.get_series().id

    # src = Source.get(1)
    video_path = src.path

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "file is not accessible..."

    # mistake_path = '/media/masoud/HDD-8TB/volleyball/wrong_annotation'
    width, height, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    previous_state = 'no-play'
    current_state = None
    no_play_flag = 0
    state_manager = Manager(
        base_dir=base_dir,
        match_id=match_id,
        series_id=series_id,
        fps=30,
        width=width,
        height=height,
        buffer_size=30
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
                    if prev == 'no-play' or prev == 'service':
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                        # state_manager.reset_short_term()
                    elif prev == 'play':

                        # In the middle of `play`, we never get `service` unless the model is wrong.
                        # we save the video to investigate the case.
                        state_manager.keep(current_frames, current_fnos, [current]*len(current_frames))
                        # state_manager.write_video(mistake_path)
                        print("Mistake .....")
                        state_manager.reset_long_buffer()
                        # Reset states, keep the current frames, but removing previous frames.
                case 'play':
                    if prev == 'service':
                        # Save the state buffer as the service video and keep buffering the rest ...
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames),
                                           set_serve_last_frame=True)
                        # state_manager.reset_short_term()
                    elif prev == 'play':
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                    elif prev == 'no-play':
                        # TODO: Check this part, not making problems.
                        state_manager.keep(current_frames, current_fnos, [current]*len(current_frames))
                case 'no-play':
                    # Only 2 consecutive "no-play" means the end of rally...
                    if prev == 'service' or prev == 'play':
                        # if we haven't got 2 cons
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                        # store the whole game video from service to end of the game.
                    elif prev == 'no-play':
                        # This is when we have 2 states of 'no-plays', so let's store the video.
                        # if the state before prev is 'service', save it as a service, if `play`,
                        # store it as a `rally`, otherwise keep skipping the video.
                        if prev_prev == 'play':
                            state_manager.db_store(draw_label=True)

                        elif prev_prev == 'service':
                            # It's either ACE, or SERVICE ERROR.
                            # TODO: We have to save it as a rally first, then insert the service...
                            state_manager.keep(current_frames, current_fnos, [current] * len(current_frames),
                                               set_serve_last_frame=True)
                            state_manager.db_store(draw_label=True)
                            state_manager.reset_long_buffer()
                        else:
                            state_manager.reset_long_buffer()
                    state_manager.reset_temp_buffer()
        else:
            continue
