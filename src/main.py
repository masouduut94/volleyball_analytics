"""
This code gets the match and video data from db, and runs the ML processing pipeline that consists of
video classification model (HuggingFace VideoMAE) and Volleyball-Specific object detection models
(Ultralytics Yolov8) on the fetched video file.
Then the statistics and outputs are stored on the db to get ready for visualization.

"""

import cv2
import numpy as np
from tqdm import tqdm
from pathlib import Path
from typing_extensions import List

from backend.app.enums.enums import GameState
from ml_manager import MLManager


def main():
    """
    team1_id=7 team2_id=8 series_id=2 video_id=4 id=1

    Returns
    -------

    """
    # Initialize ML Manager (no YAML config needed)
    ml_manager = MLManager(verbose=True)
    
    # match_id = 1
    api_base_url = "http://localhost:8000"
    
    # Initialize state manager (you may need to update this to work without YAML)
    # For now, we'll create a simple state tracking system
    state_manager = SimpleStateManager(api_base_url)
    
    cap = cv2.VideoCapture(state_manager.video.path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    assert cap.isOpened(), "file is not accessible..."
    n_frames = int(cap.get(7))
    pbar = tqdm(list(range(4950, n_frames)))

    for fno in pbar:
        pbar.update(1)
        cap.set(1, fno)
        status, frame = cap.read()
        state_manager.append_frame(frame, fno)

        if state_manager.is_full():
            current_frames, current_fnos = state_manager.get_current_frames_and_fnos()
            
            # Use ML Manager for game state classification
            try:
                game_state = ml_manager.classify_game_state(current_frames)
                state_manager.update_state_from_ml(game_state)
            except RuntimeError as e:
                print(f"Game state classification failed: {e}")
                # Fallback to previous logic if needed
                state_manager.update_state(current_frames)

            current = state_manager.current_state
            previous = state_manager.previous_state
            previous2 = state_manager.before_previous_state
            pbar.set_description(f"state: {current}")

            match current:
                case GameState.SERVICE:
                    if previous in [GameState.NO_PLAY, GameState.SERVICE, GameState.PLAY]:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))

                case GameState.PLAY:
                    if previous == GameState.SERVICE:
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                        if state_manager.service_last_frame is None:
                            state_manager.service_last_frame = len(state_manager.long_buffer_fno) - 1
                    elif previous in (GameState.PLAY, GameState.NO_PLAY):
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))

                case GameState.NO_PLAY:
                    if previous in (GameState.SERVICE, GameState.PLAY):
                        state_manager.keep(current_frames, current_fnos, [current] * len(current_frames))
                    elif previous == GameState.NO_PLAY:
                        if previous2 in (GameState.PLAY, GameState.SERVICE):
                            all_labels: List[int] = state_manager.get_labels()
                            all_frames: List[np.ndarray] = state_manager.get_long_buffer()
                            all_fnos: List[int] = state_manager.get_long_buffer_fno()
                            start_frame = all_fnos[0]
                            rally_name: Path = state_manager.get_path(start_frame, video_type='rally')
                            state_manager.write_video(
                                path=rally_name,
                                width=width,
                                height=height,
                                fps=fps,
                                labels=all_labels,
                                long_buffer=all_frames,
                                long_buffer_fno=all_fnos,
                                draw_label=True
                            )
                            rally_schema = state_manager.db_store(
                                rally_name, all_fnos, state_manager.service_last_frame, all_labels
                            )
                            
                            # Use ML Manager for object detection
                            vb_objects = predict_objects_with_ml_manager(ml_manager, all_frames)
                            done = state_manager.save_objects(rally_schema, vb_objects)
                            print(f'{rally_name} saved: {done} ...')
                            state_manager.rally_counter += 1
                            state_manager.reset_long_buffer()
                        elif previous2 == GameState.NO_PLAY:
                            state_manager.reset_long_buffer()
                    state_manager.reset_temp_buffer()
        else:
            continue
    
    # Cleanup
    ml_manager.cleanup()
    cap.release()


def predict_objects_with_ml_manager(ml_manager: MLManager, frames: List[np.ndarray]):
    """
    Use ML Manager to predict objects in frames.
    
    Args:
        ml_manager: Initialized ML Manager instance
        frames: List of frames to process
        
    Returns:
        Dictionary containing detected objects
    """
    all_objects = {
        'balls': [],
        'actions': [],
        'players': []
    }
    
    for frame in frames:
        try:
            # Ball detection
            ball_results = ml_manager.detect_ball(frame)
            all_objects['balls'].extend(ball_results)
            
            # Action detection
            action_results = ml_manager.detect_actions(frame)
            for action_type, detections in action_results.items():
                all_objects['actions'].extend(detections)
            
            # Player detection
            player_results = ml_manager.detect_players(frame)
            all_objects['players'].extend(player_results)
            
        except RuntimeError as e:
            print(f"Object detection failed for frame: {e}")
    
    return all_objects


class SimpleStateManager:
    """
    Simplified state manager for demonstration.
    You may need to implement or adapt this based on your existing state management.
    """
    
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.video = type('Video', (), {'path': 'path/to/video.mp4'})()  # Placeholder
        self.buffer_size = 30
        self.temp_buffer = []
        self.long_buffer = []
        self.long_buffer_fno = []
        self.current_state = GameState.NO_PLAY
        self.previous_state = GameState.NO_PLAY
        self.before_previous_state = GameState.NO_PLAY
        self.service_last_frame = None
        self.rally_counter = 0
    
    def append_frame(self, frame, fno):
        self.temp_buffer.append(frame)
    
    def is_full(self):
        return len(self.temp_buffer) >= self.buffer_size
    
    def get_current_frames_and_fnos(self):
        return self.temp_buffer, list(range(len(self.temp_buffer)))
    
    def update_state_from_ml(self, game_state):
        self.before_previous_state = self.previous_state
        self.previous_state = self.current_state
        self.current_state = game_state
    
    def update_state(self, frames):
        # Placeholder implementation
        pass
    
    def keep(self, frames, fnos, labels):
        self.long_buffer.extend(frames)
        self.long_buffer_fno.extend(fnos)
    
    def get_labels(self):
        return [1] * len(self.long_buffer)  # Placeholder
    
    def get_long_buffer(self):
        return self.long_buffer
    
    def get_long_buffer_fno(self):
        return self.long_buffer_fno
    
    def get_path(self, start_frame, video_type):
        return Path(f"outputs/{video_type}_{start_frame}.mp4")
    
    def write_video(self, path, width, height, fps, labels, long_buffer, long_buffer_fno, draw_label):
        # Placeholder implementation
        pass
    
    def db_store(self, path, fnos, service_frame, labels):
        # Placeholder implementation
        return {}
    
    def save_objects(self, schema, objects):
        # Placeholder implementation
        return True
    
    def reset_long_buffer(self):
        self.long_buffer.clear()
        self.long_buffer_fno.clear()
    
    def reset_temp_buffer(self):
        self.temp_buffer.clear()


if __name__ == '__main__':
    main()
