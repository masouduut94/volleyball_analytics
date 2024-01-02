from uuid import uuid1

import cv2
from time import time

import yaml
from tqdm import tqdm
from os import makedirs
from os.path import join
from pathlib import Path
from tqdm import tqdm
from api.models import Source, Service, Rally
# from api.data_classes import SourceData, ServiceData
from gamestate_detection import GameStateDetector

FPS = 30


def slice_video(serve_detection_model: GameStateDetector, video, output_path, buffer_size=30):
    cap = cv2.VideoCapture(video)
    assert cap.isOpened(), f'the video file is not opening {video}'
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    id_buffer = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    pbar = tqdm(total=n_frames, desc='processing rally #1')
    serves_index_buffer = []
    rally_counter = 0

    codec = cv2.VideoWriter_fourcc(*'mp4v')
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
    filename = join(output_path, Path(video).stem + f'_visualization.mp4')
    writer = cv2.VideoWriter(filename, codec, fps, (w, h))

    while status:
        status, frame = cap.read()
        if not status:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pbar.update(1)
        frame_id = int(cap.get(1))
        buffer.append(frame)
        id_buffer.append(frame_id)

        if len(buffer) != buffer_size:
            continue

        label = serve_detection_model.predict(buffer)
        if label == 'serve':
            start_frame_id = id_buffer[0]
            serves_index_buffer.append(start_frame_id)
            rally_counter += 1
            pbar.set_description(f'processing rally #{rally_counter}')
        id_buffer.clear()
        buffer.clear()

    pbar.close()

    # When we have the start and end frame indexes, we start writing the video slices.
    for i, _ in enumerate(tqdm(serves_index_buffer[:-1], desc='writing videos')):
        start = serves_index_buffer[i]
        end = serves_index_buffer[i + 1]

        codec = cv2.VideoWriter_fourcc(*'mp4v')
        w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
        filename = join(output_path, Path(video).stem + f'{start}_{end}.mp4')
        writer = cv2.VideoWriter(filename, codec, fps, (w, h))
        # cap.set(1, start)
        for i in range(start, end):
            cap.set(1, i)
            status, frame = cap.read()
            writer.write(frame)
        writer.release()


def annotate_service(serve_detection_model: GameStateDetector, video_path, output_path, buffer_size=30):
    video_path = Path(video_path)
    cap = cv2.VideoCapture(video_path.as_posix())
    assert video_path.is_file(), f'file {video_path.as_posix()} not found...'
    assert cap.isOpened(), f'the video file is not opening {video_path}'
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    buffer2 = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    pbar = tqdm(total=n_frames, desc=f'writing 0/{n_frames}')

    codec = cv2.VideoWriter_fourcc(*'mp4v')
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
    filename = join(output_path, Path(video_path).stem + f'_visualization.mp4')
    writer = cv2.VideoWriter(filename, codec, fps, (w, h))
    t2 = 0
    t1 = 0
    while status:
        status, frame = cap.read()
        fno = int(cap.get(1))
        if not status:
            break
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pbar.update(1)
        buffer.append(frame)
        buffer2.append(fno)

        if len(buffer) != buffer_size:
            continue
        else:
            t1 = time()
            label = serve_detection_model.predict(buffer)
            t2 = time()
            pbar.set_description(f'processing {fno}/{n_frames} | p-time: {abs(t2 - t1): .3f}')

            match label:
                case 'service':
                    color = (0, 255, 0)
                case 'no-play':
                    color = (0, 0, 255)
                case 'play':
                    color = (255, 255, 0)
                case _:
                    color = (255, 255, 255)

            for f, fno in zip(buffer, buffer2):
                f = cv2.putText(
                    f, label, (w // 2, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, color, 2
                )
                f = cv2.putText(
                    f, f"Frame # {fno}/{n_frames}", (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 0, 0), 2)
                writer.write(f)
        buffer.clear()
        buffer2.clear()

    writer.release()
    cap.release()
    pbar.close()


class Manager:
    def __init__(self, fps, width, height, buffer_size):
        self.buffer_size = buffer_size
        self.states = ['no-play', 'no-play', 'no-play']
        self.long_term_buffer = []
        self.short_term_buffer = []
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.width = width
        self.height = height
        self.fps = fps

    def is_full(self):
        return len(self.short_term_buffer) == self.buffer_size

    def set_current_state(self, curr_state):
        prev = self.states[-1]
        prev_prev = self.states[-2]
        self.states[-3] = prev_prev
        self.states[-2] = prev
        self.states[-1] = curr_state

    def keep(self, frames):
        self.long_term_buffer.extend(frames)
        self.reset_short_term()

    def append(self, frame):
        self.short_term_buffer.append(frame)

    def get_current_frames(self):
        return self.short_term_buffer

    def get_all_frames(self):
        return self.long_term_buffer

    def reset_short_term(self):
        self.short_term_buffer.clear()

    def reset_long_term(self):
        self.long_term_buffer.clear()

    def write_video(self, path):
        random = str(uuid1())[:8]
        name = Path(path) / f'{random}.mp4'
        writer = cv2.VideoWriter(
            name.as_posix(), self.codec, self.fps, (self.width, self.height)
        )
        for f in self.long_term_buffer:
            writer.write(f)
        writer.release()

    @property
    def current(self):
        return self.states[-1]

    @property
    def prev(self):
        return self.states[-2]

    @property
    def prev_prev(self):
        return self.states[-3]

    def reset(self):
        self.states = ['no-play', 'no-play', 'no-play']


if __name__ == '__main__':
    # ckpt = "/home/masoud/Desktop/projects/volleyball_analytics/weights/game-status/services-650/checkpoint-3744"
    config = '/home/masoud/Desktop/projects/volleyball_analytics/conf/ml_models.yaml'
    cfg = yaml.load(open(config), Loader=yaml.SafeLoader)
    model = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])
    src = Source.get(1)
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
        state_manager.append(frame)

        if state_manager.is_full():
            current_frames = state_manager.get_current_frames()
            current_state = model.predict(current_frames)
            state_manager.set_current_state(current_state)
            pbar.set_description(f"state: {current_state}")
            current = state_manager.current
            prev = state_manager.prev
            prev_prev = state_manager.prev_prev

            match current:
                case 'service':
                    if prev == 'no-play' or prev == 'service':
                        state_manager.keep(current_frames)
                        state_manager.reset_short_term()
                    elif prev == 'play':
                        # In the middle of `play`, we never get `service` unless the model is wrong.
                        # we save the video to investigate the case.
                        state_manager.keep(current_frames)
                        state_manager.write_video(mistake_path)
                        print("Mistake .....")
                        state_manager.reset_short_term()
                        state_manager.reset_long_term()
                        # Reset states, keep the current frames, but removing previous frames.
                        state_manager.keep(current_frames)
                case 'play':
                    if prev == 'service':
                        # Save the state buffer as the service video and keep buffering the rest ...
                        state_manager.keep(current_frames)
                        state_manager.write_video(service_save_path)
                        print(f"Caught a service... saved in {service_save_path}")

                        state_manager.reset_short_term()
                    elif prev == 'play':
                        state_manager.keep(current_frames)
                        state_manager.reset_short_term()
                    elif prev == 'no-play':
                        # TODO: Check this part, not making problems.
                        state_manager.keep(current_frames)
                        state_manager.reset_short_term()
                case 'no-play':
                    # Only 2 consecutive "no-play" means the end of rally...
                    if prev == 'service' or prev == 'play':
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
                            state_manager.reset_long_term()
                    state_manager.reset_short_term()
        else:
            continue
