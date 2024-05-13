import cv2
import yaml
from tqdm import tqdm
from gamestate_detection import GameStateDetector
from src.backend.app.models.models import Video
from src.ml.video_mae.game_state.utils import Manager

if __name__ == '__main__':
    config = 'conf/ml_models.yaml'
    cfg = yaml.load(open(config), Loader=yaml.SafeLoader)
    model = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])
    src = Video.get(1)
    video = src.path

    cap = cv2.VideoCapture(video)
    assert cap.isOpened(), "file is not accessible..."

    rally_save_path = '/media/HDD/DATA/volleyball/rallies'
    service_save_path = '/media/HDD/DATA/volleyball/serves'
    mistake_path = '/media/HDD/DATA/volleyball/wrong_annotation'

    width, height, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    previous_state = 'no-play'
    current_state = None
    no_play_flag = 0
    state_manager = Manager(fps, width, height, 30)
    pbar = tqdm(list(range(n_frames)))
    for fno in pbar:
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        state_manager.append_frame(frame)

        if state_manager.is_full():
            current_frames = state_manager.get_current_frames_and_fnos()
            current_state = model.predict(current_frames)
            state_manager._set_current_state(current_state)
            pbar.set_description(f"state: {current_state}")
            current = state_manager.current_state
            prev = state_manager.previous_state
            prev_prev = state_manager.before_previous_state

            match current:
                case 'service':
                    if prev in ('no-play', 'service'):
                        state_manager.keep(current_frames)
                        state_manager.reset_temp_buffer()
                    elif prev == 'play':
                        # In the middle of `play`, we never get `service` unless the model is wrong.
                        # we save the video to investigate the case.
                        state_manager.keep(current_frames)
                        state_manager.write_video(mistake_path)
                        print("Mistake .....")
                        state_manager.reset_temp_buffer()
                        state_manager.reset_long_buffer()
                        # Reset states, keep the current frames, but removing previous frames.
                        state_manager.keep(current_frames)
                case 'play':
                    if prev == 'service':
                        # Save the state buffer as the service video and keep buffering the rest ...
                        state_manager.keep(current_frames)
                        state_manager.write_video(service_save_path)
                        print(f"Caught a service... saved in {service_save_path}")

                        state_manager.reset_temp_buffer()
                    elif prev == 'play':
                        state_manager.keep(current_frames)
                        state_manager.reset_temp_buffer()
                    elif prev == 'no-play':
                        # TODO: Check this part, not making problems.
                        state_manager.keep(current_frames)
                        state_manager.reset_temp_buffer()
                case 'no-play':
                    # Only 2 consecutive "no-play" means the end of rally...
                    if prev in ('service', 'play'):
                        # if we haven't got 2 cons
                        state_manager.keep(current_frames)
                        # store the whole game video from service to end of the game.
                    elif prev == 'no-play':
                        # This is when we have 2 states of 'no-plays', so let's store the video.
                        # if the state before prev is 'service', save it as a service, if `play`,
                        # store it as a `rally`, otherwise keep skipping the video.
                        if prev_prev == 'play':
                            state_manager.write_video(rally_save_path)
                            print(f"Caught a RALLY ... saved in {rally_save_path}")

                        elif prev_prev == 'service':
                            state_manager.write_video(service_save_path)
                            print(f"Caught a SERVICE ... saved in {service_save_path}")
                        else:
                            state_manager.reset_long_buffer()
                    state_manager.reset_temp_buffer()
        else:
            continue
