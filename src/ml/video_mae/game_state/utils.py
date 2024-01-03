from os import makedirs
from os.path import join
from time import time
from uuid import uuid1

import cv2
from tqdm import tqdm

from gamestate_detection import GameStateDetector
from pathlib import Path


class Manager:
    def __init__(self, fps: int, width: int, height: int, buffer_size: int):
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
