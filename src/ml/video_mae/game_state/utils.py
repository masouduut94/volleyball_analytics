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
        self.temp_buffer = []
        self.temp_buffer_fno = []
        self.long_buffer = []
        self.long_buffer_fno = []
        self.service_frames = []
        self.labels = []

        self.service_last_frame = None

        self.service_fnos = []

        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.width = width
        self.height = height
        self.fps = fps

        self.serve_counter = 0
        self.rally_counter = 0

    def is_full(self):
        return len(self.temp_buffer) == self.buffer_size

    def set_current_state(self, curr_state):
        prev = self.states[-1]
        prev_prev = self.states[-2]
        self.states[-3] = prev_prev
        self.states[-2] = prev
        self.states[-1] = curr_state

    def keep(self, frames, fnos, states, set_serve_last_frame=False):
        self.long_buffer.extend(frames)
        self.long_buffer_fno.extend(fnos)
        self.labels.extend(states)
        if set_serve_last_frame:
            self.service_last_frame = len(self.long_buffer_fno) - 1
        self.reset_temp_buffer()

    def append_frame(self, frame, fno):
        self.temp_buffer.append(frame)
        self.temp_buffer_fno.append(fno)

    def get_current_frames_and_fnos(self):
        return self.temp_buffer, self.temp_buffer_fno

    def reset_temp_buffer(self):
        self.temp_buffer.clear()
        self.temp_buffer_fno.clear()

    def reset_long_buffer(self):
        self.long_buffer.clear()
        self.long_buffer_fno.clear()
        self.labels.clear()
        self.service_last_frame = None

    def db_store(self, draw_label: bool = False):
        rally_name = Path(self.rally_dir) / f'rally_{self.rally_counter}.mp4'
        writer = cv2.VideoWriter(
            rally_name.as_posix(), self.codec, self.fps, (self.width, self.height)
        )
        if draw_label:
            for label, frame, fno in zip(self.labels, self.long_buffer, self.long_buffer_fno):
                match label:
                    case "service":
                        color = (0, 255, 0)
                    case "play":
                        color = (0, 255, 255)
                    case _:
                        color = (255, 0, 0)
                frame = cv2.putText(frame, label, (100, 50), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                frame = cv2.putText(frame, str(fno), (self.width - 400, 50), cv2.FONT_HERSHEY_PLAIN, 2,
                                    (255, 0, 0), 2)
                writer.write(frame)
        else:
            for frame in self.long_buffer:
                writer.write(frame)
        writer.release()

        rally_1st_frame = self.long_buffer_fno[0]
        rally_last_frame = self.long_buffer_fno[-1]
        rally_vdata = VideoData(match_id=self.match_id, path=rally_name.as_posix(), camera_type=1, type='rally')
        rally_video_db = Video.save(rally_vdata.to_dict())
        rally_data = RallyData(match_id=self.match_id, start_frame=rally_1st_frame, end_frame=rally_last_frame,
                               video_id=rally_video_db.id)
        rally = Rally.save(rally_data.to_dict())
        self.rally_counter += 1
        self.serve_counter += 1
        print(f"rally is saved in {rally_name.name}...\n")
        # write service video and save it in DB...
        if self.service_last_frame is not None:
            serve_name = Path(self.service_dir) / f'serve_{self.serve_counter}.mp4'
            writer = cv2.VideoWriter(serve_name.as_posix(), self.codec, self.fps, (self.width, self.height))
            serve_1st_frame = self.long_buffer_fno[0]
            serve_last_frame = self.long_buffer_fno[self.service_last_frame]
            serve_frames = self.long_buffer[:self.service_last_frame]
            for frame in serve_frames:
                writer.write(frame)
            writer.release()
            serve_vdata = VideoData(match_id=self.match_id, path=serve_name.as_posix(), camera_type=1, type='serve')
            serve_video_db = Video.save(serve_vdata.to_dict())
            service_data = ServiceData(rally_id=rally.id, start_frame=serve_1st_frame, end_frame=serve_last_frame,
                                       video_id=serve_video_db.id)
            Service.save(service_data.to_dict())
            print(f"serve is saved in {serve_name.name}...\n")

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
