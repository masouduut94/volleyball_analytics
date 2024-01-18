from typing import List

import cv2
from time import time

import numpy as np
from tqdm import tqdm
from uuid import uuid1
from os import makedirs
from pathlib import Path, PosixPath
from os.path import join

from unsync import unsync

from api.data_classes import ServiceData, RallyData, VideoData
from api.enums import ServiceType
from api.models import Video, Rally
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector
from src.utilities.utils import timeit


class Manager:
    def __init__(self, cfg: dict, series_id: int, cap: cv2.VideoCapture, buffer_size: int, video_name: str):
        self.state_detector = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])
        self.vb_object_detector = VolleyBallObjectDetector(config=cfg, video_name=video_name, use_player_detection=True)
        self.base_dir = cfg['base_dir']
        self.match_id = cfg['match_id']
        self.series_id = series_id

        self.rally_base_dir = f'{self.base_dir}/{self.series_id}/{self.match_id}/rallies/'
        makedirs(self.rally_base_dir, exist_ok=True)

        self.buffer_size = buffer_size
        self.states = ['no-play', 'no-play', 'no-play']
        # Buffers
        self.temp_buffer = []
        self.temp_buffer_fno = []
        self.long_buffer = []
        self.long_buffer_fno = []
        self.labels = []
        self.service_last_frame = None

        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.width = int(cap.get(3))
        self.height = int(cap.get(4))
        self.fps = int(cap.get(5))
        self.rally_counter = 0

    # @timeit
    def predict_state(self, frames):
        current_state = self.state_detector.predict(frames)
        self._set_current_state(current_state)
        return current_state

    @timeit
    def predict_objects(self, frames):
        batch_size = 30
        # d, r = divmod(len(frames), batch_size)
        d = len(frames) // batch_size
        results = []
        for i in range(d+1):
            temp = frames[batch_size*i: batch_size*(i+1)]
            if len(temp):
                batch_balls = self.vb_object_detector.detect_balls(temp)
                batch_vb_objects = self.vb_object_detector.detect_actions(temp, exclude='ball')
                batch_results = []
                for balls, vb_objects in zip(batch_balls, batch_vb_objects):
                    vb_objects['ball'] = balls
                    batch_results.append(vb_objects)
                results.extend(batch_results)
        return results

    def is_full(self):
        return len(self.temp_buffer) == self.buffer_size

    def get_long_buffer(self):
        return self.long_buffer

    def get_long_buffer_fno(self):
        return self.long_buffer_fno

    def get_labels(self):
        return self.labels

    def get_path(self, fno, video_type='rally'):
        return Path(self.rally_base_dir) / f'{video_type}_{self.rally_counter}_start_frame_{fno}.mp4'

    def _set_current_state(self, curr_state):
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
            if self.service_last_frame is not None:
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

    @unsync
    def write_video(self, path: PosixPath, labels: List[str], long_buffer: List[np.ndarray],
                    long_buffer_fno: List[int], draw_label: bool = False):
        writer = cv2.VideoWriter(path.as_posix(), self.codec, self.fps, (self.width, self.height))
        if draw_label:
            for label, frame, fno in zip(labels, long_buffer, long_buffer_fno):
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
            for frame in long_buffer:
                writer.write(frame)
        writer.release()
        return True

    def db_store(self, rally_name, frame_numbers, service_last_frame=None, labels=None):
        """
        Saves a video of the rally, and also creates DB-related items. (video, and rally)

        """

        rally_1st_frame = frame_numbers[0]
        rally_last_frame = frame_numbers[-1]
        rally_vdata = VideoData(match_id=self.match_id, path=rally_name.as_posix(), camera_type=1, type='rally')
        rally_video_db = Video.save(rally_vdata.to_dict())

        service_data = ServiceData(end_frame=service_last_frame, ball_positions={}, hitter="Igor Kliuka",
                                   serving_region=None, bounce_point=[120, 200], target_zone=5,
                                   type=ServiceType.HIGH_TOSS)

        rally_data = RallyData(match_id=self.match_id, video_id=rally_video_db.id, start_frame=rally_1st_frame,
                               end_frame=rally_last_frame, rally_states=str(labels), service=service_data.to_dict())
        rally = Rally.save(rally_data.to_dict())
        return rally

    def yolo_run(self, rally: Rally, gpu: bool = True):
        video_path = rally.video

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
