import cv2
import numpy as np
from tqdm import tqdm
from time import time
from os import makedirs
from os.path import join
from pathlib import Path
from typing_extensions import List, Dict, Tuple

from src.backend.app.api_interface import APIInterface
from src.backend.app.enums.enums import GameState, ServiceType
from src.utilities.utils import timeit, BoundingBox, ProjectLogger, state_summarize
from src.backend.app.schemas import services, rallies, matches, series, videos
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector


class Manager:
    def __init__(self, cfg: dict, url: str, buffer_size: int):
        """
        Args:
            cfg(dict): dictionary of configs for the project.
            buffer_size: buffer size that keeps the frames for
                         ML operations.
        """
        self.api_interface = APIInterface(url=url)
        self.state_detector = GameStateDetector(cfg=cfg['video_mae']['game_state_3'])

        self.match: matches.MatchCreateSchema = self.api_interface.get_match(match_id=int(cfg['match_id']))
        self.video: videos.VideoCreateSchema = self.api_interface.get_video(video_id=self.match.video_id)
        self.tournament: series.SeriesBaseSchema = self.api_interface.get_series(series_id=self.match.series_id)

        video_name = self.video.video_name()
        self.vb_object_detector = VolleyBallObjectDetector(
            config=cfg, video_name=video_name, use_player_detection=True
        )

        self.base_dir = cfg['base_dir']
        self.rally_base_dir = f'{self.base_dir}/{self.tournament.id}/{self.match.id}/rallies/'
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
        self.rally_counter = 0

    # @timeit
    def update_state(self, frames: List[np.ndarray]):
        """This function gets a list (with constant number) of frames for
        1 second, and updates the game state. It's important
        to note that we currently work on videos with 30-50 fps.

        Args:
            frames:

        """
        # TODO: Update the state detection to operate in more complex situations like 5 states.
        current_state = self.state_detector.predict(frames)
        self._set_current_state(current_state)

    @timeit
    def predict_objects(self, frames: List[np.ndarray]) -> List[Dict[str, List[BoundingBox]]]:
        """Runs the yolo model object detection on the frames. (batch inference)

        Args:
            frames: List of numpy.ndarray

        Returns:
            List of dictionaries indicating objects found in each frame (frame numbers are the keys).

        """
        batch_size = 50
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
        """Checks if the size of temporary buffer is equal to size of 30 frames
        in a second or not.

        Returns:
            True if buffer is full.

        """
        return len(self.temp_buffer) == self.buffer_size

    def get_long_buffer(self) -> List[np.ndarray]:
        return self.long_buffer

    def get_long_buffer_fno(self) -> List[int]:
        return self.long_buffer_fno

    def get_labels(self) -> List[int]:
        return self.labels

    def get_path(self, fno: int, video_type: str = 'rally') -> Path:
        """Given the frame number, and the video type, outputs a storage
        directory for clipped videos.

        Args:
            fno:
            video_type:

        Returns:
            The path to output rally clip.
        -------

        """
        return Path(self.rally_base_dir) / f'{video_type}_{self.rally_counter}_start_frame_{fno}.mp4'

    def _set_current_state(self, curr_state: int):
        """substitute the 3 consecutive states after getting the current
         state.(each state consists of 30 frames.)

        Args:
            curr_state

        """
        prev = self.states[-1]
        prev_prev = self.states[-2]
        self.states[-3] = prev_prev
        self.states[-2] = prev
        self.states[-1] = curr_state

    def keep(self, frames: List[np.ndarray], fnos: List[int], states: List[int]):
        """Attach the current frames, frame numbers and states to
        the end of the long buffer.

        Args:
            frames: list of frames
            fnos: list of frame numbers.
            states: list of states.

        """
        self.long_buffer.extend(frames)
        self.long_buffer_fno.extend(fnos)
        self.labels.extend(states)
        self.reset_temp_buffer()

    def append_frame(self, frame: np.ndarray, fno: int):
        """Appends the video frames and frame numbers to the temporary buffer.

        Args:
            frame:
            fno:

        Returns
        -------

        """
        self.temp_buffer.append(frame)
        self.temp_buffer_fno.append(fno)

    def get_current_frames_and_fnos(self) -> Tuple[List[np.ndarray], List[int]]:
        """Just a getter method for getting currently buffered frames and frame
        numbers together.

        Returns:
            list of frames, and list of frame numbers.
        """
        return self.temp_buffer, self.temp_buffer_fno

    def reset_temp_buffer(self):
        """Reset the frame buffers that keep the current frames."""

        self.temp_buffer.clear()
        self.temp_buffer_fno.clear()

    def reset_long_buffer(self):
        """Resets the video frame storage that saves the rally videos."""

        self.long_buffer.clear()
        self.long_buffer_fno.clear()
        self.labels.clear()
        self.service_last_frame = None

    @staticmethod
    def write_video(
            path: Path, width: int, height: int, fps: int, labels: List[int],
            long_buffer: List[np.ndarray], long_buffer_fno: List[int], draw_label: bool = False
    ):
        """It handles the creation of rally video along with the attaching the labels...

        Args:
            width: output width
            height: output height
            fps: output video fps
            path: path to save the video.
            labels: list of the output labels for the video frames...
            long_buffer: list of frames to be written
            long_buffer_fno: List of the frame numbers.
            draw_label: Whether to write the video labels or not...

        Returns:
             true if it finishes without problem.

        """
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(path.as_posix(), codec, fps, (width, height))
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
                frame = cv2.putText(frame, str(fno), (width - 400, 50), cv2.FONT_HERSHEY_PLAIN, 2,
                                    (255, 0, 0), 2)
                writer.write(frame)
        else:
            for frame in long_buffer:
                writer.write(frame)
        writer.release()

    def db_store(self, rally_name: Path, frame_numbers: List[int], service_ending_index: int = None,
                 labels: List[int] = None) -> rallies.RallyBaseSchema:
        """Saves rally information on DB and returns the object.

        Args:
            rally_name: The name of the video.
            frame_numbers: List of the frame numbers accumulated by the manager.
            service_ending_index: The index of the frame where the serve beginning is detected.
            labels: The list of the detected game status for each frame.

        Returns:
            The rally object that is stored in the DB.

        """
        rally_1st_frame = frame_numbers[0]
        rally_last_frame = frame_numbers[-1]
        labels = state_summarize(labels)
        service_end_frame = rally_1st_frame + service_ending_index if service_ending_index is not None else None

        service_data = services.ServiceCreateSchema(
            end_frame=service_end_frame, end_index=service_ending_index, hitter="Igor",
            hitter_bbox={}, bounce_point={'x': 120, 'y': 200}, target_zone=5, type=ServiceType.HIGH_TOSS
        )
        rally_data = rallies.RallyCreateSchema(
            match_id=self.match.id, start_frame=rally_1st_frame, end_frame=rally_last_frame, order=self.rally_counter,
            rally_states=str(labels), service=service_data.model_dump(), clip_path=str(rally_name)
        )
        rally: rallies.RallyBaseSchema = self.api_interface.insert_rally(**rally_data.model_dump())
        return rally

    @property
    def current_state(self) -> int:
        return self.states[-1]

    @property
    def previous_state(self) -> int:
        return self.states[-2]

    @property
    def before_previous_state(self) -> int:
        """ Returns the value of 3rd state before the current state."""
        return self.states[-3]

    def reset(self):
        self.states = [GameState.NO_PLAY, GameState.NO_PLAY, GameState.NO_PLAY]

    def save_objects(self, rally_schema: rallies.RallyBaseSchema, batch_vb_objects: List[Dict[str, List[BoundingBox]]]):
        """It converts the Yolo detected objects into Json-serializable
        objects and saves it in DB.

        Args:
            rally_schema: rally table ORM object that is going to attach the yolo objects to it.
            batch_vb_objects: yolo objects for all frames in a rally.

        Returns:
            True if all done without problem.

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

        rally_schema.blocks = blocks_js
        rally_schema.sets = sets_js
        rally_schema.spikes = spikes_js
        rally_schema.ball_positions = balls_js
        rally_schema.receives = receives_js

        updated = self.api_interface.rally_update(rally_schema)
        return updated


def annotate_service(
        serve_detection_model: GameStateDetector, video_path: str, output_path: str, buffer_size: int = 30
):
    """Annotates the video frames based on the game-state detector detections.

    Args:
        serve_detection_model: The initialized game-state detection model.
        video_path: Path to the input video.
        output_path: path to save the output video.
        buffer_size: Size of the game-state detection model input.

    """
    logger = ProjectLogger()
    video_path = Path(video_path)
    cap = cv2.VideoCapture(video_path.as_posix())
    assert video_path.is_file(), logger.critical(f'file {video_path.as_posix()} not found...')
    assert cap.isOpened(), logger.critical(f'the video file is not opening {video_path}')
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    buffer2 = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    pbar = tqdm(total=n_frames, desc=f'writing 0/{n_frames}')
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
    output_name = join(output_path, f'{Path(video_path).stem}_visualization.mp4')
    writer = cv2.VideoWriter(output_name, codec, fps, (w, h))
    logger.success("process initialized successfully...")

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
    logger.success(f"Done. Saved as {output_name} ...")
