import cv2
import numpy as np
from tqdm import tqdm
from time import time
from os import makedirs
from pathlib import Path
from os.path import join
from typing_extensions import List, Dict, Tuple

# from unsync import unsync

from api.models import Rally
from api.enums import ServiceType, GameState
from src.utilities.utils import timeit, BoundingBox, state_changes
from api.schemas import ServiceData, RallyData
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector


class Manager:
    def __init__(self, cfg: dict, series_id: int, cap: cv2.VideoCapture, buffer_size: int, video_name: str):
        """

        Parameters
        ----------
        cfg(dict): dictionary of configs for the project.
        series_id: It's the tournament series id from database.
        cap: OpenCV videoCapture object
        buffer_size: It's the size of the buffer that keeps the video frames for ML operations.
        video_name: It is used for finding the court corners on the court.json file.
        """
        self.state_detector = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])
        self.vb_object_detector = VolleyBallObjectDetector(config=cfg, video_name=video_name, use_player_detection=True)
        self.base_dir = cfg['base_dir']
        self.match_id = cfg['match_id']
        self.series_id = series_id

        self.rally_base_dir = f'{self.base_dir}/{self.series_id}/{self.match_id}/rallies/'
        makedirs(self.rally_base_dir, exist_ok=True)

        self.buffer_size = buffer_size
        self.states = [GameState.NO_PLAY, GameState.NO_PLAY, GameState.NO_PLAY]
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
    def predict_state(self, frames: List[np.ndarray]):
        """
        It gets a list of frames and outputs the label of the game state.
        It's important to note that we currently work on videos with 30 fps,
        so the input is a list of 30 frames.
        Parameters
        ----------
        frames

        Returns
        -------

        """
        current_state = self.state_detector.predict(frames)
        self._set_current_state(current_state)
        return current_state

    @timeit
    def predict_objects(self, frames: List[np.ndarray]) -> List[Dict[str, List[BoundingBox]]]:
        """
        Runs the yolo model object detection on the frames. (batch inference)
        Parameters
        ----------
        frames: List of numpy.ndarray

        Returns
        -------

        """
        batch_size = 30
        d = len(frames) // batch_size
        results = []
        for i in range(d + 1):
            temp = frames[batch_size * i: batch_size * (i + 1)]
            if len(temp):
                batch_balls = self.vb_object_detector.detect_balls(temp)
                batch_vb_objects = self.vb_object_detector.detect_actions(temp, exclude='ball')
                batch_results = []
                for balls, vb_objects in zip(batch_balls, batch_vb_objects):
                    vb_objects['ball'] = balls
                    batch_results.append(vb_objects)
                results.extend(batch_results)
        return results

    def is_full(self) -> bool:
        """
        Checks if the size of temporary buffer is equal to size of 30 frames in a second or not.
        Returns
        -------

        """
        return len(self.temp_buffer) == self.buffer_size

    def get_long_buffer(self) -> List[np.ndarray]:
        return self.long_buffer

    def get_long_buffer_fno(self) -> List[int]:
        return self.long_buffer_fno

    def get_labels(self) -> List[int]:
        return self.labels

    def get_path(self, fno: int, video_type: str = 'rally') -> Path:
        """
        Given the frame number, and the video type, outputs a storage directory for clipped videos.
        Parameters
        ----------
        fno
        video_type

        Returns
        -------

        """
        return Path(self.rally_base_dir) / f'{video_type}_{self.rally_counter}_start_frame_{fno}.mp4'

    def _set_current_state(self, curr_state: int):
        """
        substitute the 3 consecutive states after getting the current state.(each state consists
        of 30 frames.)
        Parameters
        ----------
        curr_state

        Returns
        -------

        """
        prev = self.states[-1]
        prev_prev = self.states[-2]
        self.states[-3] = prev_prev
        self.states[-2] = prev
        self.states[-1] = curr_state

    def keep(self, frames: List[np.ndarray], fnos: List[int], states: List[int]):
        """
        Attach the current frames, frame numbers and states to the end of the long buffer.
        Parameters
        ----------
        frames: list of frames
        fnos: list of frame numbers.
        states: list of states.

        -------

        """
        self.long_buffer.extend(frames)
        self.long_buffer_fno.extend(fnos)
        self.labels.extend(states)
        self.reset_temp_buffer()

    def append_frame(self, frame: np.ndarray, fno: int):
        """
        Appends the video frames and frame numbers to the temporary buffer.
        Parameters
        ----------
        frame
        fno

        Returns
        -------

        """
        self.temp_buffer.append(frame)
        self.temp_buffer_fno.append(fno)

    def get_current_frames_and_fnos(self) -> Tuple[List[np.ndarray], List[int]]:
        """
        Just a getter method for getting frames and frame numbers together.
        Returns
        -------

        """
        return self.temp_buffer, self.temp_buffer_fno

    def reset_temp_buffer(self):
        """
        Reset the frame buffers that keep the current frames.

        Returns
        -------

        """
        self.temp_buffer.clear()
        self.temp_buffer_fno.clear()

    def reset_long_buffer(self):
        """
        Resets the video frame storage that saves the rally videos.
        Returns
        -------

        """
        self.long_buffer.clear()
        self.long_buffer_fno.clear()
        self.labels.clear()
        self.service_last_frame = None

    def write_video(self, path: Path, labels: List[int], long_buffer: List[np.ndarray],
                    long_buffer_fno: List[int], draw_label: bool = False):
        """
        It handles the creation of rally video along with the attaching the labels...
        Parameters
        ----------
        path: path to save the file.
        labels: list of the output labels for the video frames...
        long_buffer: list of frames to be written
        long_buffer_fno: List of the frame numbers.
        draw_label: Whether to write the video labels or not...

        Returns true after work is done.
        -------

        """
        writer = cv2.VideoWriter(path.as_posix(), self.codec, self.fps, (self.width, self.height))
        if draw_label:
            for label, frame, fno in zip(labels, long_buffer, long_buffer_fno):
                match label:
                    case GameState.SERVICE:
                        string = 'service'
                        color = (0, 255, 0)
                    case GameState.PLAY:
                        string = 'play'
                        color = (0, 255, 255)
                    case _:
                        string = 'no-play'
                        color = (255, 0, 0)
                frame = cv2.putText(frame, string, (100, 50), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                frame = cv2.putText(frame, str(fno), (self.width - 400, 50), cv2.FONT_HERSHEY_PLAIN, 2,
                                    (255, 0, 0), 2)
                writer.write(frame)
        else:
            for frame in long_buffer:
                writer.write(frame)
        writer.release()

    def db_store(self, rally_name: Path, frame_numbers: List[int], service_ending_index: int = None,
                 labels: List[int] = None):
        """
        Saves a video of the rally, and also creates DB-related items. (video, and rally)

        """
        rally_1st_frame = frame_numbers[0]
        rally_last_frame = frame_numbers[-1]
        labels = state_changes(labels)
        # rally_vdata = VideoData(path=rally_name.as_posix(), camera_type=1)
        # rally_video_db = Video.save(rally_vdata.model_dump())
        service_end_frame = rally_1st_frame + service_ending_index if service_ending_index is not None else None

        service_data = ServiceData(
            end_frame=service_end_frame, end_index=service_ending_index, hitter="Igor Kliuka",
            hitter_bbox={}, bounce_point=[120, 200], target_zone=5, type=ServiceType.HIGH_TOSS
        )
        rally_data = RallyData(
            match_id=self.match_id, start_frame=rally_1st_frame, end_frame=rally_last_frame,
            rally_states=str(labels), service=service_data.model_dump(), clip_path=str(rally_name)
        )
        rally = Rally.save(rally_data.model_dump())
        return rally

    @property
    def current(self) -> int:
        return self.states[-1]

    @property
    def prev(self) -> int:
        return self.states[-2]

    @property
    def prev_prev(self) -> int:
        return self.states[-3]

    def reset(self):
        self.states = [GameState.NO_PLAY, GameState.NO_PLAY, GameState.NO_PLAY]

    @staticmethod
    def save_objects(rally_db: Rally, batch_vb_objects: List[Dict[str, List[BoundingBox]]]):
        """
        It converts the Yolo detected objects into Json-serializable objects and saves it in DB.

        Parameters
        ----------
        rally_db: rally table ORM object that is going to attach the yolo objects to it.
        batch_vb_objects: yolo objects for all frames in a rally.

        Returns
        -------

        """
        balls_js = {}
        blocks_js = {}
        sets_js = {}
        spikes_js = {}
        receives_js = {}

        for i, objects in enumerate(batch_vb_objects):
            balls = [obj.xyxy_dict for obj in objects['ball']]
            blocks = [obj.xyxy_dict for obj in objects['block']]
            sets = [obj.xyxy_dict for obj in objects['set']]
            spikes = [obj.xyxy_dict for obj in objects['spike']]
            receives = [obj.xyxy_dict for obj in objects['receive']]
            if len(balls):
                balls_js[i] = balls
            if len(blocks):
                blocks_js[i] = blocks
            if len(sets):
                sets_js[i] = sets
            if len(spikes):
                spikes_js[i] = spikes
            if len(receives):
                receives_js[i] = receives

        rally_db.update({"blocks": blocks_js, 'sets': sets_js, "spikes": spikes_js, "ball_positions": balls_js,
                         "receives": receives_js})


def annotate_service(serve_detection_model: GameStateDetector, video_path: str, output_path: str,
                     buffer_size: int = 30):
    """
    Annotates the video frames based on the game-state detector detections.
    Parameters
    ----------
    serve_detection_model: The initialized game-state detection model.
    video_path: Path to the input video.
    output_path: path to save the output video.
    buffer_size: Size of the game-state detection model input.

    Returns
    -------

    """
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
    output_name = join(output_path, Path(video_path).stem + f'_visualization.mp4')
    writer = cv2.VideoWriter(output_name, codec, fps, (w, h))

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
                case GameState.SERVICE:
                    color = (0, 255, 0)
                case GameState.NO_PLAY:
                    color = (0, 0, 255)
                case GameState.PLAY:
                    color = (255, 255, 0)
                case _:
                    color = (255, 255, 255)

            for f, fno in zip(buffer, buffer2):
                f = cv2.putText(f, serve_detection_model.state2label[label].upper(), (w // 2, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 2)
                f = cv2.putText(f, f"Frame # {fno}/{n_frames}".upper(), (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (255, 0, 0), 2)
                writer.write(f)
        buffer.clear()
        buffer2.clear()

    writer.release()
    cap.release()
    pbar.close()
    print(f"Done. Saved as {output_name} ...")
