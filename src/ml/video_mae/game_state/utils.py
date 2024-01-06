import cv2
from time import time
from tqdm import tqdm
from uuid import uuid1
from os import makedirs
from pathlib import Path
from os.path import join

from api.data_classes import ServiceData, RallyData, VideoData
from api.models import Video, Rally, Service
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector


class Manager:
    def __init__(self, base_dir: str, match_id: int, series_id: int, fps: int, width: int, height: int,
                 buffer_size: int):
        self.base_dir = base_dir
        self.match_id = match_id
        self.series_id = series_id

        self.rally_dir = f'{self.base_dir}/{self.series_id}/{self.match_id}/rallies/'
        self.service_dir = f'{self.base_dir}/{self.series_id}/{self.match_id}/services/'
        makedirs(self.rally_dir, exist_ok=True)
        makedirs(self.service_dir, exist_ok=True)

        self.buffer_size = buffer_size
        self.states = ['no-play', 'no-play', 'no-play']
        # Buffers
        self.short_term_buffer = []
        self.short_fno_buffer = []
        self.long_term_buffer = []
        self.long_fno_buffer = []
        self.service_frames = []

        self.service_last_frame = None

        self.service_fnos = []

        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.width = width
        self.height = height
        self.fps = fps

        self.serve_counter = 0
        self.rally_counter = 0

    def is_full(self):
        return len(self.short_term_buffer) == self.buffer_size

    def set_current_state(self, curr_state):
        prev = self.states[-1]
        prev_prev = self.states[-2]
        self.states[-3] = prev_prev
        self.states[-2] = prev
        self.states[-1] = curr_state

    def keep(self, frames, fnos, set_serve_last_frame=False):
        self.long_term_buffer.extend(frames)
        self.long_fno_buffer.extend(fnos)
        if set_serve_last_frame:
            self.service_last_frame = len(self.long_fno_buffer) - 1  # last frame number of
        self.reset_short_term()

    def append_frame(self, frame, fno):
        self.short_term_buffer.append(frame)
        self.short_fno_buffer.append(fno)

    def get_current_frames_and_fnos(self):
        return self.short_term_buffer, self.short_fno_buffer

    def reset_short_term(self):
        self.short_term_buffer.clear()
        self.short_fno_buffer.clear()

    def reset_long_term(self):
        self.long_term_buffer.clear()
        self.long_fno_buffer.clear()
        self.service_last_frame = None

    def output_video(self):
        # 1. Saving the videos
        service_filename = Path(self.service_dir) / f'serve_{self.serve_counter}.mp4'
        writer = cv2.VideoWriter(
            service_filename.as_posix(), self.codec, self.fps, (self.width, self.height)
        )
        serve_frames = self.long_term_buffer[:self.service_last_frame]
        for f in serve_frames:
            writer.write(f)
        writer.release()

        rally_filename = Path(self.rally_dir) / f'rally_{self.rally_counter}.mp4'
        writer = cv2.VideoWriter(
            rally_filename.as_posix(), self.codec, self.fps, (self.width, self.height)
        )
        for f in self.long_term_buffer:
            writer.write(f)
        writer.release()
        # 1.1 updating the counters.
        self.serve_counter += 1
        self.rally_counter += 1
        # 2. Inserting into DB.
        # 2.1 Get start_frame, last_frame ...
        serve_1st_frame = self.long_fno_buffer[0]
        # TODO: If service last frame is none, there must be some mistake with model output...
        serve_last_frame = self.long_fno_buffer[self.service_last_frame]
        rally_1st_frame = self.long_fno_buffer[0]
        rally_last_frame = self.long_fno_buffer[-1]
        # 2.2 create video data for rally and service ...
        rally_video_data = VideoData(match_id=self.match_id, path=rally_filename.as_posix(), camera_type=1,
                                     type='rally')
        rally_video_db = Video.save(rally_video_data.to_dict())
        serve_video_data = VideoData(match_id=self.match_id, path=service_filename.as_posix(), camera_type=1,
                                     type='serve')
        serve_video_db = Video.save(serve_video_data.to_dict())

        rally_data = RallyData(
            match_id=self.match_id,
            start_frame=rally_1st_frame,
            end_frame=rally_last_frame,
            video_id=rally_video_db.id
        )
        rally = Rally.save(rally_data.to_dict())
        print("rally is saved ...")
        service_data = ServiceData(
            rally_id=rally.id,
            start_frame=serve_1st_frame,
            end_frame=serve_last_frame,
            video_id=serve_video_db.id
        )
        Service.save(service_data.to_dict())
        self.service_last_frame = None

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
