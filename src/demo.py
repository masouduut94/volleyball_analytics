"""Enhanced Volleyball Analytics Demo

This demo showcases advanced volleyball analytics capabilities including:
- Object detection (ball, players, actions) with ML Manager
- Game state classification using VideoMAE
- Ball trajectory visualization with N consecutive frames
- Professional player visualization using supervision library
- Enhanced tracking and analysis features
"""

import cv2
import numpy as np
from tqdm import tqdm
from time import time, sleep
from os import makedirs
from os.path import join
from pathlib import Path
from argparse import ArgumentParser
from typing import List, Dict, Any, Tuple, Optional
from collections import deque
import supervision as sv

from ml_manager import MLManager
from ml_manager.utils.logger import logger


class VolleyballAnalyticsDemo:
    """Advanced volleyball analytics demo with comprehensive visualization."""
    
    def __init__(self, 
                 ml_manager: MLManager,
                 ball_trajectory_frames: int = 10,
                 buffer_size: int = 30):
        """Initialize the demo class.
        
        Args:
            ml_manager: Initialized ML Manager instance
            ball_trajectory_frames: Number of consecutive frames to show ball trail
            buffer_size: Buffer size for game state classification
        """
        self.ml_manager = ml_manager
        self.ball_trajectory_frames = ball_trajectory_frames
        self.buffer_size = buffer_size
        
        # Initialize tracking storage
        self.ball_trajectories = deque(maxlen=ball_trajectory_frames)
        self.frame_buffer = []
        self.frame_numbers = []
        
        # Initialize supervision components
        self.ball_annotator = sv.BoxAnnotator(
            color=sv.Color.GREEN,
            thickness=3,
            text_thickness=2,
            text_scale=0.8
        )
        
        self.player_annotator = sv.BoxAnnotator(
            color=sv.Color.BLUE,
            thickness=2,
            text_thickness=1,
            text_scale=0.6
        )
        
        # Create a more sophisticated tracker for players (pedestrian-style)
        self.tracker = sv.ByteTracker(
            track_activation_threshold=0.25,
            lost_track_buffer=30,
            minimum_matching_threshold=0.8,
            frame_rate=30
        )
        
        # Initialize trajectory smoothing
        self.trajectory_smoother = sv.TraceTail(
            length=ball_trajectory_frames,
            thickness=3,
            color=sv.Color.GREEN
        )
        
        # Game state visualization
        self.game_state_history = deque(maxlen=10)
        
        logger.info(f"Demo initialized with ball trajectory frames: {ball_trajectory_frames}")
    
    def process_frame(self, frame: np.ndarray, frame_number: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process a single frame with all detection and visualization.
    
        Args:
            frame: Input frame
            frame_number: Current frame number

        Returns:
                Tuple of (annotated_frame, processing_results)
        """
        start_time = time()
        results = {
            'frame_number': frame_number,
                'ball_detections': [],
                'player_detections': [],
                'action_detections': [],
            'game_state': 'unknown',
            'processing_time': 0.0
        }
        
        try:
            # 1. Object Detection
            ball_detections = self.ml_manager.detect_ball(frame, conf_threshold=0.3)
            player_keypoints = self.ml_manager.detect_players(frame, conf_threshold=0.25)
            action_detections = self.ml_manager.detect_actions(
                frame, 
                exclude=['ball'], 
                conf_threshold=0.25
            )
            
            # Convert detections to supervision format
            ball_sv_detections = self._convert_ball_detections_to_sv(ball_detections)
            player_sv_detections = self._convert_player_detections_to_sv(player_keypoints)
            
            # Update tracker with player detections
            tracked_players = self.tracker.update_with_detections(player_sv_detections)
            
            # Store ball trajectory
            if len(ball_detections) > 0:
                ball_center = ball_detections[0].bbox.center
                self.ball_trajectories.append((ball_center[0], ball_center[1], frame_number))
            
            # 2. Annotate frame
            annotated_frame = self._annotate_frame(
                frame=frame,
                ball_detections=ball_sv_detections,
                tracked_players=tracked_players,
                action_detections=action_detections,
                frame_number=frame_number
            )
            
            # Store results
            results['ball_detections'] = ball_detections
            results['player_detections'] = player_keypoints
            results['action_detections'] = action_detections
        
        except Exception as e:
                logger.error(f"Error processing frame {frame_number}: {e}")
                annotated_frame = frame.copy()

        results['processing_time'] = time() - start_time
        return annotated_frame, results

    def process_buffer_for_game_state(self, buffer: List[np.ndarray], frame_numbers: List[int]) -> str:
        """Process buffer for game state classification.
    
        Args:
            buffer: List of frames
                frame_numbers: Corresponding frame numbers

        Returns:
                Predicted game state
        """
        try:
            if len(buffer) >= self.buffer_size:
                game_state_result = self.ml_manager.classify_game_state(buffer)
                if hasattr(game_state_result, 'predicted_class'):
                    game_state = game_state_result.predicted_class.value
                    self.game_state_history.append((game_state, frame_numbers[-1]))
                    return game_state
        except Exception as e:
            logger.warning(f"Game state classification failed: {e}")
        
        return 'unknown'
    
    def _convert_ball_detections_to_sv(self, detections) -> sv.Detections:
        """Convert ball detections to supervision format."""
        if not detections:
            return sv.Detections.empty()
        
        xyxy = []
        confidence = []
        class_id = []
        
        for det in detections:
            if hasattr(det, 'bbox'):
                bbox = det.bbox
                xyxy.append([bbox.x1, bbox.y1, bbox.x2, bbox.y2])
                confidence.append(det.confidence)
                class_id.append(0)  # Ball class
        
        if xyxy:
            return sv.Detections(
                xyxy=np.array(xyxy),
                confidence=np.array(confidence),
                class_id=np.array(class_id)
            )
        return sv.Detections.empty()
    
    def _convert_player_detections_to_sv(self, player_keypoints) -> sv.Detections:
        """Convert player detections to supervision format."""
        if not player_keypoints:
            return sv.Detections.empty()
        
        xyxy = []
        confidence = []
        class_id = []
        
        for player_kp in player_keypoints:
            if hasattr(player_kp, 'bbox') and player_kp.bbox:
                bbox = player_kp.bbox
                xyxy.append([bbox.x1, bbox.y1, bbox.x2, bbox.y2])
                confidence.append(player_kp.confidence)
                class_id.append(1)  # Player class
        
        if xyxy:
            return sv.Detections(
                xyxy=np.array(xyxy),
                confidence=np.array(confidence),
                class_id=np.array(class_id)
            )
        return sv.Detections.empty()
    
    def _annotate_frame(self, 
                       frame: np.ndarray,
                       ball_detections: sv.Detections,
                       tracked_players: sv.Detections,
                       action_detections: List,
                       frame_number: int) -> np.ndarray:
        """Annotate frame with all detections and visualizations."""
        annotated_frame = frame.copy()
        
        # 1. Draw ball detections with supervision
        if len(ball_detections) > 0:
            ball_labels = [f"Ball {conf:.2f}" for conf in ball_detections.confidence]
            annotated_frame = self.ball_annotator.annotate(
                scene=annotated_frame,
                detections=ball_detections,
                labels=ball_labels
            )
        
        # 2. Draw player tracking with supervision (pedestrian-style)
        if len(tracked_players) > 0:
            # Create labels with track IDs
            player_labels = []
            if tracked_players.tracker_id is not None:
                for tracker_id, conf in zip(tracked_players.tracker_id, tracked_players.confidence):
                    player_labels.append(f"Player #{tracker_id} {conf:.2f}")
            else:
                player_labels = [f"Player {conf:.2f}" for conf in tracked_players.confidence]
            
            annotated_frame = self.player_annotator.annotate(
                scene=annotated_frame,
                detections=tracked_players,
                labels=player_labels
            )
            
            # Add trajectory trails for players
            annotated_frame = self.trajectory_smoother.annotate(
                scene=annotated_frame,
                detections=tracked_players
            )
        
        # 3. Draw ball trajectory with N consecutive frames
        annotated_frame = self._draw_ball_trajectory(annotated_frame, frame_number)
        
        # 4. Draw action detections (if any)
        annotated_frame = self._draw_action_detections(annotated_frame, action_detections)
        
        # 5. Draw game state information
        annotated_frame = self._draw_game_state_info(annotated_frame, frame_number)
        
        # 6. Draw frame information
        annotated_frame = self._draw_frame_info(annotated_frame, frame_number)
        
        return annotated_frame
    
    def _draw_ball_trajectory(self, frame: np.ndarray, frame_number: int) -> np.ndarray:
        """Draw ball trajectory for N consecutive frames."""
        if len(self.ball_trajectories) < 2:
            return frame
        
        # Convert trajectory to numpy array
        trajectory_points = list(self.ball_trajectories)
        
        # Create colors that fade from old to new
        num_points = len(trajectory_points)
        
        for i in range(1, num_points):
            # Calculate alpha based on age of trajectory point
            alpha = (i / num_points) * 255
            color = (0, int(alpha), 0)  # Green with varying intensity
            
            pt1 = (int(trajectory_points[i-1][0]), int(trajectory_points[i-1][1]))
            pt2 = (int(trajectory_points[i][0]), int(trajectory_points[i][1]))
            
            # Draw line segment
            cv2.line(frame, pt1, pt2, color, max(1, int(alpha/50)))
            
            # Draw circle at each point
            cv2.circle(frame, pt2, max(2, int(alpha/40)), color, -1)
        
        # Draw current ball position with larger circle
        if trajectory_points:
            current_pos = (int(trajectory_points[-1][0]), int(trajectory_points[-1][1]))
            cv2.circle(frame, current_pos, 8, (0, 255, 0), -1)
            
            # Add trajectory statistics
            if len(trajectory_points) >= 2:
                last_pt = trajectory_points[-1]
                prev_pt = trajectory_points[-2]
                velocity = np.sqrt((last_pt[0] - prev_pt[0])**2 + (last_pt[1] - prev_pt[1])**2)
                
                # Draw velocity info
                cv2.putText(frame, f"Ball Speed: {velocity:.1f} px/frame", 
                           (current_pos[0] + 15, current_pos[1] - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def _draw_action_detections(self, frame: np.ndarray, action_detections: List) -> np.ndarray:
        """Draw action detection results."""
        action_colors = {
            'spike': (255, 0, 255),    # Magenta
            'set': (255, 255, 0),      # Cyan
            'serve': (255, 165, 0),    # Orange
            'receive': (128, 0, 128),  # Purple
            'block': (0, 255, 255)     # Yellow
        }
        
        if isinstance(action_detections, dict):
            for action_type, detections in action_detections.items():
                if isinstance(detections, list):
                    for det in detections:
                        if hasattr(det, 'bbox'):
                            bbox = det.bbox
                            color = action_colors.get(action_type, (128, 128, 128))
                            
                            # Draw bounding box
                            cv2.rectangle(frame, 
                                        (int(bbox.x1), int(bbox.y1)), 
                                        (int(bbox.x2), int(bbox.y2)), 
                                        color, 2)
                            
                            # Draw label
                            label = f"{action_type}: {det.confidence:.2f}"
                            cv2.putText(frame, label,
                                       (int(bbox.x1), int(bbox.y1) - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
    
    def _draw_game_state_info(self, frame: np.ndarray, frame_number: int) -> np.ndarray:
        """Draw game state information."""
        current_game_state = 'unknown'
        if self.game_state_history:
            current_game_state = self.game_state_history[-1][0]
        
        # Game state color mapping
        state_colors = {
            'serve': (0, 255, 0),     # Green
            'play': (255, 255, 0),    # Yellow  
            'no_play': (0, 0, 255),   # Red
            'unknown': (255, 255, 255) # White
        }
        
        color = state_colors.get(current_game_state.lower(), state_colors['unknown'])
        
        # Draw game state
        state_text = f"Game State: {current_game_state.upper()}"
        text_size = cv2.getTextSize(state_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
        
        # Background rectangle
        cv2.rectangle(frame, (20, 20), (text_size[0] + 40, 80), (0, 0, 0), -1)
        cv2.putText(frame, state_text, (30, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        
        return frame
    
    def _draw_frame_info(self, frame: np.ndarray, frame_number: int) -> np.ndarray:
        """Draw frame information."""
        h, w = frame.shape[:2]
        
        # Frame info
        frame_info = f"Frame: {frame_number}"
        ball_count = len(self.ball_trajectories)
        trajectory_info = f"Ball Trail: {ball_count}/{self.ball_trajectory_frames}"
        
        # Position at top-right
        info_text = f"{frame_info} | {trajectory_info}"
        text_size = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        
        # Background
        cv2.rectangle(frame, 
                     (w - text_size[0] - 20, 10), 
                     (w - 10, 50), 
                     (0, 0, 0), -1)
        
        cv2.putText(frame, info_text, (w - text_size[0] - 15, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame


def parse_args():
    """Parse command line arguments."""
    parser = ArgumentParser(description="Enhanced Volleyball Analytics Demo")
    
    parser.add_argument(
        '--video_path',
        type=str,
        required=True,
        help='Path to input video file'
    )
    
    parser.add_argument(
        '--output_path', 
        type=str,
        default="runs/demo_output",
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--ball_trajectory_frames',
        type=int,
        default=15,
        help='Number of consecutive frames to show ball trajectory (N parameter)'
    )
    
    parser.add_argument(
        '--buffer_size',
        type=int,
        default=30,
        help='Buffer size for game state classification'
    )
    
    parser.add_argument(
        '--conf_threshold',
        type=float,
        default=0.25,
        help='Confidence threshold for detections'
    )
    
    parser.add_argument(
        '--save_video',
        action='store_true',
        help='Save output video'
    )
    
    parser.add_argument(
        '--display_video',
        action='store_true', 
        help='Display video during processing'
    )
    
    parser.add_argument(
        '--fps_limit',
        type=int,
        default=None,
        help='Limit processing FPS (for real-time display)'
    )
    
    return parser.parse_args()


def main():
    """Main demo function."""
    args = parse_args()

    # Validate inputs
    video_path = Path(args.video_path)
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return
    
    output_path = Path(args.output_path)
    makedirs(output_path, exist_ok=True)
    
    logger.info("=== Enhanced Volleyball Analytics Demo ===")
    logger.info(f"Video: {video_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Ball trajectory frames: {args.ball_trajectory_frames}")

    # Initialize ML Manager
    logger.info("Initializing ML Manager...")
    try:
        ml_manager = MLManager(device='cuda' if cv2.cuda.getCudaEnabledDeviceCount() > 0 else 'cpu')
        model_status = ml_manager.get_model_status()
        logger.info(f"Model status: {model_status}")
    except Exception as e:
        logger.error(f"Failed to initialize ML Manager: {e}")
        return
    
    # Initialize demo class
    demo = VolleyballAnalyticsDemo(
        ml_manager=ml_manager,
        ball_trajectory_frames=args.ball_trajectory_frames,
        buffer_size=args.buffer_size
    )

    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video properties: {width}x{height}, {fps} FPS, {frame_count} frames")
    
    # Initialize video writer if saving
    writer = None
    if args.save_video:
        output_video_path = output_path / f"{video_path.stem}_enhanced_demo.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))
        logger.info(f"Output video: {output_video_path}")
    
    # Processing variables
    frame_buffer = []
    frame_numbers = []
    current_frame = 0
    processing_stats = {
        'total_frames': 0,
        'avg_processing_time': 0.0,
        'total_processing_time': 0.0
    }
    
    # Progress bar
    pbar = tqdm(total=frame_count, desc="Processing frames")
    
    # FPS limiting for real-time display
    if args.fps_limit:
        frame_delay = 1.0 / args.fps_limit
    else:
        frame_delay = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_frame += 1
            frame_start_time = time()
            
            # Process frame
            annotated_frame, results = demo.process_frame(frame, current_frame)
            
            # Add to buffer for game state classification
            frame_buffer.append(frame)
            frame_numbers.append(current_frame)
            
            # Process game state when buffer is full
            if len(frame_buffer) >= args.buffer_size:
                game_state = demo.process_buffer_for_game_state(frame_buffer, frame_numbers)
                # Keep only recent frames in buffer
                frame_buffer = frame_buffer[-args.buffer_size//2:]
                frame_numbers = frame_numbers[-args.buffer_size//2:]
            
            # Update statistics
            processing_stats['total_frames'] += 1
            processing_stats['total_processing_time'] += results['processing_time']
            processing_stats['avg_processing_time'] = (
                processing_stats['total_processing_time'] / processing_stats['total_frames']
            )
            
            # Save frame if writing video
            if writer:
                writer.write(annotated_frame)
            
            # Display frame if requested
            if args.display_video:
                cv2.imshow('Volleyball Analytics', annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("User requested quit")
                    break
                elif key == ord('s'):
                    # Save current frame
                    frame_path = output_path / f"frame_{current_frame:06d}.jpg"
                    cv2.imwrite(str(frame_path), annotated_frame)
                    logger.info(f"Saved frame: {frame_path}")
                
                # Update progress
            pbar.set_description(
                f"Frame {current_frame}/{frame_count} | "
                f"Avg: {processing_stats['avg_processing_time']:.3f}s | "
                f"FPS: {1.0/processing_stats['avg_processing_time']:.1f}"
            )
            pbar.update(1)
            
            # FPS limiting
            if frame_delay > 0:
                elapsed = time() - frame_start_time
                if elapsed < frame_delay:
                    sleep(frame_delay - elapsed)
        
        # Process remaining buffer
        if frame_buffer:
            demo.process_buffer_for_game_state(frame_buffer, frame_numbers)

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
    finally:
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        if args.display_video:
            cv2.destroyAllWindows()
        pbar.close()

    # Final statistics
    logger.info("=== Processing Complete ===")
    logger.info(f"Processed {processing_stats['total_frames']} frames")
    logger.info(f"Average processing time: {processing_stats['avg_processing_time']:.3f} seconds")
    logger.info(f"Average FPS: {1.0/processing_stats['avg_processing_time']:.1f}")
    logger.info(f"Total processing time: {processing_stats['total_processing_time']:.2f} seconds")
    
    if args.save_video:
        logger.success(f"Enhanced video saved to: {output_path}")
    
    # Cleanup ML Manager
    ml_manager.cleanup()
    logger.success("Demo completed successfully!")


if __name__ == '__main__':
    main()
