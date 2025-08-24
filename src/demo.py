"""
Enhanced Volleyball Analytics Demo

This demo showcases the full capabilities of the ML Manager including:
- Game state classification
- Ball detection and tracking
- Player detection and tracking
- Action detection
- Enhanced visualization with trajectories and game state
"""

import cv2
import numpy as np
from tqdm import tqdm
from time import time
from os import makedirs
from os.path import join
from pathlib import Path
from argparse import ArgumentParser
from typing import List, Dict, Any

from utilities.utils import ProjectLogger
from ml_manager import MLManager


def parse_args():
    parser = ArgumentParser("Enhanced volleyball analytics demo with tracking and visualization...")
    parser.add_argument(
        '--video_path',
        type=str,
        default="data/raw/videos/train/16.mp4"
    )
    parser.add_argument(
        '--output_path',
        type=str,
        default="runs/DEMO"
    )
    parser.add_argument(
        '--buffer_size',
        type=int,
        default=30
    )
    parser.add_argument(
        '--show_trajectories',
        action='store_true',
        help='Show object trajectories'
    )
    parser.add_argument(
        '--save_plots',
        action='store_true',
        help='Save trajectory and tracking plots'
    )
    parser.add_argument(
        '--tracking_method',
        type=str,
        default='norfair',
        choices=['norfair', 'sort', 'custom'],
        help='Tracking method to use'
    )
    return parser.parse_args()





def process_frame_with_ml_manager(ml_manager: MLManager, 
                                frame: np.ndarray,
                                frame_number: int,
                                show_trajectories: bool = True) -> Dict[str, Any]:
    """
    Process a single frame using the ML Manager.
    
    Args:
        ml_manager: Initialized ML Manager instance
        frame: Input frame
        frame_number: Current frame number
        show_trajectories: Whether to show trajectories
        
    Returns:
        Dictionary containing all processing results
    """
    results = {
        'frame': frame,
        'frame_number': frame_number,
        'detections': [],
        'tracked_objects': [],
        'game_state': 'unknown',
        'game_state_confidence': 0.0,
        'ball_trajectory': [],
        'processing_time': 0.0
    }
    
    start_time = time()
    
    try:
        # 1. Detect objects (ball, players, actions)
        ball_detections = ml_manager.detect_ball(frame, conf_threshold=0.25, iou_threshold=0.45)
        player_detections = ml_manager.detect_players(frame, conf_threshold=0.25, iou_threshold=0.45)
        action_detections = ml_manager.detect_actions(frame, exclude=['ball'], conf_threshold=0.25, iou_threshold=0.45)
        
        # Combine all detections
        all_detections = []
        
        # Add ball detections
        for ball in ball_detections:
            if hasattr(ball, 'bbox'):
                all_detections.append({
                    'bbox': ball.bbox,
                    'confidence': ball.confidence,
                    'name': 'ball'
                })
        
        # Add player detections
        for player in player_detections:
            if hasattr(player, 'bbox'):
                all_detections.append({
                    'bbox': player.bbox,
                    'confidence': player.confidence,
                    'name': 'person'
                })
        
        # Add action detections
        for action_type, detections in action_detections.items():
            for detection in detections:
                if hasattr(detection, 'bbox'):
                    all_detections.append({
                        'bbox': detection.bbox,
                        'confidence': detection.confidence,
                        'name': action_type
                    })
        
        results['detections'] = all_detections
        
        # 2. Track objects
        if all_detections:
            tracked_objects = ml_manager.track_objects(frame, all_detections, frame_number)
            results['tracked_objects'] = tracked_objects
            
            # Get ball trajectory
            ball_trajectory = ml_manager.get_ball_trajectory()
            results['ball_trajectory'] = ball_trajectory
        
        # 3. Game state classification (will be done in batch processing)
        
    except Exception as e:
        print(f"Error processing frame {frame_number}: {e}")
    
    results['processing_time'] = time() - start_time
    return results


def process_buffer_with_ml_manager(ml_manager: MLManager,
                                 buffer: List[np.ndarray],
                                 frame_numbers: List[int],
                                 show_trajectories: bool = True) -> Dict[str, Any]:
    """
    Process a buffer of frames for game state classification.
    
    Args:
        ml_manager: Initialized ML Manager instance
        buffer: List of frames
        frame_numbers: List of frame numbers
        show_trajectories: Whether to show trajectories
        
    Returns:
        Dictionary containing buffer processing results
    """
    results = {
        'frames': buffer,
        'frame_numbers': frame_numbers,
        'game_state': 'unknown',
        'game_state_confidence': 0.0,
        'frame_results': []
    }
    
    try:
        # 1. Game state classification on buffer
        game_state_result = ml_manager.classify_game_state(buffer)
        if hasattr(game_state_result, 'predicted_label'):
            results['game_state'] = game_state_result.predicted_label
            results['game_state_confidence'] = game_state_result.confidence
        else:
            results['game_state'] = 'unknown'
            results['game_state_confidence'] = 0.0
        
        # 2. Process individual frames
        for i, (frame, frame_number) in enumerate(zip(buffer, frame_numbers)):
            frame_result = process_frame_with_ml_manager(
                ml_manager, frame, frame_number, show_trajectories
            )
            results['frame_results'].append(frame_result)
            
    except Exception as e:
        print(f"Error processing buffer: {e}")
    
    return results


def visualize_results(ml_manager: MLManager,
                     frame: np.ndarray,
                     detections: List[Dict[str, Any]],
                     tracked_objects: List[Dict[str, Any]],
                     game_state: str,
                     frame_info: str,
                     ball_trajectory: List[tuple] = None) -> np.ndarray:
    """
    Visualize all results on a frame.
    
    Args:
        ml_manager: ML Manager instance
        frame: Input frame
        detections: Detection results
        tracked_objects: Tracking results
        game_state: Game state
        frame_info: Frame information
        ball_trajectory: Ball trajectory points
        
    Returns:
        Frame with all visualizations
    """
    # Use ML Manager's visualization capabilities
    result_frame = ml_manager.visualize_frame(
        frame=frame,
        detections=detections,
        tracked_objects=tracked_objects,
        game_state=game_state,
        frame_info=frame_info
    )
    
    # Add ball trajectory if available
    if ball_trajectory and len(ball_trajectory) > 1:
        result_frame = ml_manager.visualizer.draw_ball_trajectory(
            result_frame, ball_trajectory
        )
    
    return result_frame


def main():
    """Main demo function."""
    logger = ProjectLogger(filename="logs.log")
    args = parse_args()

    video_path = Path(args.video_path)
    output_path = Path(args.output_path)

    # Initialize ML Manager
    logger.info("Initializing ML Manager with enhanced capabilities...")
    ml_manager = MLManager(verbose=True)
    logger.info("ML Manager initialized successfully.")

    # Check model availability
    model_status = ml_manager.get_model_status()
    logger.info(f"Model status: {model_status}")

    # Open video
    cap = cv2.VideoCapture(video_path.as_posix())
    assert video_path.is_file(), logger.info(f'File {video_path.as_posix()} not found...')
    assert cap.isOpened(), logger.info(f'The video file is not opening {video_path}')
    
    # Create output directory
    makedirs(args.output_path, exist_ok=True)

    # Video properties
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    
    # Initialize video writer
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    output_name = join(args.output_path, f'{Path(video_path).stem}_ENHANCED_DEMO.mp4')
    writer = cv2.VideoWriter(output_name, codec, fps, (w, h))
    
    # Initialize tracking
    logger.info("Initializing tracking...")
    
    # Processing variables
    buffer = []
    frame_numbers = []
    frame_count = 0
    
    # Progress bar
    pbar = tqdm(total=n_frames, desc=f'Processing 0/{n_frames}')
    
    logger.success("Process initialization completed...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            pbar.update(1)
            
            # Add frame to buffer
            buffer.append(frame)
            frame_numbers.append(frame_count)

            # Process buffer when full
            if len(buffer) == args.buffer_size:
                # Process buffer
                buffer_results = process_buffer_with_ml_manager(
                    ml_manager, buffer, frame_numbers, args.show_trajectories
                )
                
                # Process each frame in buffer
                for i, frame_result in enumerate(buffer_results['frame_results']):
                    # Visualize frame
                    visualized_frame = visualize_results(
                        ml_manager=ml_manager,
                        frame=frame_result['frame'],
                        detections=frame_result['detections'],
                        tracked_objects=frame_result['tracked_objects'],
                        game_state=buffer_results['game_state'],
                        frame_info=f"Frame #{frame_result['frame_number']}/{n_frames}",
                        ball_trajectory=frame_result['ball_trajectory']
                    )
                    
                    # Write frame
                    writer.write(visualized_frame)
                
                # Clear buffer
                buffer.clear()
                frame_numbers.clear()
                
                # Update progress
                pbar.set_description(f'Processing {frame_count}/{n_frames} | '
                                  f'Game State: {buffer_results["game_state"].upper()}')

        # Process remaining frames
        if buffer:
            buffer_results = process_buffer_with_ml_manager(
                ml_manager, buffer, frame_numbers, args.show_trajectories
            )
            
            for i, frame_result in enumerate(buffer_results['frame_results']):
                visualized_frame = visualize_results(
                    ml_manager=ml_manager,
                    frame=frame_result['frame'],
                    detections=frame_result['detections'],
                    tracked_objects=frame_result['tracked_objects'],
                    game_state=buffer_results['game_state'],
                    frame_info=f"Frame #{frame_result['frame_number']}/{n_frames}",
                    ball_trajectory=frame_result['ball_trajectory']
                )
                writer.write(visualized_frame)

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
    finally:
        # Cleanup
        cap.release()
        writer.release()
        pbar.close()

    # Create summary visualizations
    if args.save_plots:
        logger.info("Creating summary visualizations...")
        
        # Ball trajectory plot
        ball_trajectory = ml_manager.get_ball_trajectory()
        if ball_trajectory:
            trajectory_plot = ml_manager.create_trajectory_plot(
                ball_trajectory,
                title="Ball Trajectory Analysis",
                save_path=join(args.output_path, "ball_trajectory.png")
            )
        
        # Tracking summary
        tracking_summary = ml_manager.create_tracking_summary(
            save_path=join(args.output_path, "tracking_summary.png")
        )
        
        logger.info("Summary visualizations created")

    # Final statistics
    tracking_stats = ml_manager.get_tracking_stats()
    logger.info(f"Tracking statistics: {tracking_stats}")
    
    logger.success(f"Process finished. Saved output as {output_name}")

    # Cleanup
    ml_manager.cleanup()


if __name__ == '__main__':
    main()
