"""
Demo script for volleyball analytics ML Manager.

This script provides two main functions:
1. run_object_detection: Detects and tracks ball with trailing path, detects actions
2. run_video_classification: Classifies game state every 30 frames and visualizes results
"""

import cv2
import numpy as np
import supervision as sv
from pathlib import Path
from ml_manager.ml_manager import MLManager


def run_object_detection(video_path: str, output_path: str) -> None:
    """
    Run object detection on video with ball tracking, action detection, and player detection.
    
    This function:
    - Loads the ML Manager
    - Detects and tracks ball with 8-frame trailing path
    - Detects actions (no tracking needed for actions)
    - Detects players and visualizes them with triangles
    - Visualizes ball with yellow circles, actions with class-specific colored boxes, and players with green triangles
    - Saves the output video
    
    Args:
        video_path: Path to input video file
        output_path: Path to save output video with visualizations
    """
    print("Initializing ML Manager...")
    ml_manager = MLManager()
    
    # Check if required models are available
    if not ml_manager.is_model_available('ball_detection'):
        raise RuntimeError("Ball detection model not available")
    if not ml_manager.is_model_available('action_detection'):
        raise RuntimeError("Action detection model not available")
    if not ml_manager.is_model_available('player_detection'):
        raise RuntimeError("Player detection model not available")
    if not ml_manager.is_model_available('tracking'):
        raise RuntimeError("Tracking module not available")
    
    print("Opening video...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Initialize supervision annotators
    ball_label_annotator = sv.LabelAnnotator(color=sv.Color.YELLOW, text_thickness=1, text_scale=0.5)
    label_annotator = sv.LabelAnnotator(text_thickness=1, text_scale=0.5)
    triangle_annotator = sv.TriangleAnnotator(color=sv.Color.GREEN)
    
    # Define colors for different action classes (class_id -> color)
    action_colors = {
        0: sv.Color.RED,
        1: sv.Color.BLUE,
        2: sv.Color.from_hex('#800080'),
        3: sv.Color.from_hex("#FFA500"),
        4: sv.Color.from_hex("#FFC0CB"),
        5: sv.Color.WHITE,
        # Add more colors if needed
    }
    
    # Tracking state
    ball_trajectory = []
    frame_count = 0
    
    print("Processing video frames...")
    while frame_count < 500:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processing frame {frame_count}/{total_frames}")
        
        # Detect all objects (actions, ball, players) using detect_all
        action_detections, ball_detection, player_detections = ml_manager.detect_all(
            frame, conf_threshold=0.25, iou_threshold=0.45
        )
        
        # Convert detections to supervision format
        ball_detections_sv = sv.Detections.empty()
        action_detections_sv = sv.Detections.empty()
        player_detections_sv = sv.Detections.empty()
        
        # Process ball detections
        if ball_detection:
            ball_boxes = []
            ball_confidences = []
            ball_class_ids = []
            
            bbox = ball_detection.bbox
            ball_boxes.append([bbox.x1, bbox.y1, bbox.x2, bbox.y2])
            ball_confidences.append(ball_detection.confidence)
            ball_class_ids.append(ball_detection.class_id)
            
            if ball_boxes:
                ball_detections_sv = sv.Detections(
                    xyxy=np.array(ball_boxes),
                    confidence=np.array(ball_confidences),
                    class_id=np.array(ball_class_ids)
                )
                
                # Update ball trajectory for tracking
                for i, bbox in enumerate(ball_boxes):
                    center_x = (bbox[0] + bbox[2]) / 2
                    center_y = (bbox[1] + bbox[3]) / 2
                    ball_trajectory.append((center_x, center_y))
            
        # Process action detections
        if action_detections:
            action_boxes = []
            action_confidences = []
            action_class_ids = []
            action_labels = []
            
            for detection in action_detections:
                bbox = detection.bbox
                action_boxes.append([bbox.x1, bbox.y1, bbox.x2, bbox.y2])
                action_confidences.append(detection.confidence)
                action_class_ids.append(detection.class_id)
                action_labels.append(f"{detection.class_name}: {detection.confidence:.2f}")
            
            if action_boxes:
                action_detections_sv = sv.Detections(
                    xyxy=np.array(action_boxes),
                    confidence=np.array(action_confidences),
                    class_id=np.array(action_class_ids)
                )
        
        # Process player detections
        if player_detections:
            player_boxes = []
            player_confidences = []
            player_class_ids = []
            player_labels = []
            
            for player in player_detections:
                if player.bbox is not None:
                    bbox = player.bbox
                    player_boxes.append([bbox.x1, bbox.y1, bbox.x2, bbox.y2])
                    player_confidences.append(player.confidence)
                    player_class_ids.append(0)  # Player class ID
                    player_labels.append(f"{player.confidence:.2f}")
            
            if player_boxes:
                player_detections_sv = sv.Detections(
                    xyxy=np.array(player_boxes),
                    confidence=np.array(player_confidences),
                    class_id=np.array(player_class_ids)
                )
            
        # Annotate frame
        annotated_frame = frame.copy()
        
        # Draw ball trajectory (8 frames trailing)
        if ball_trajectory:
            # Keep only last 8 points for trailing effect
            recent_trajectory = ball_trajectory[-8:]
            if len(recent_trajectory) > 1:
                # Draw trajectory line using OpenCV
                for i in range(1, len(recent_trajectory)):
                    # Calculate alpha (transparency) for fading effect
                    alpha = i / len(recent_trajectory)
                    thickness = max(1, int(3 * alpha))
                    
                    # Convert points to integers
                    pt1 = (int(recent_trajectory[i-1][0]), int(recent_trajectory[i-1][1]))
                    pt2 = (int(recent_trajectory[i][0]), int(recent_trajectory[i][1]))
                    
                    # Draw line segment with varying thickness for trailing effect
                    cv2.line(annotated_frame, pt1, pt2, (0, 255, 255), thickness)  # Yellow trail
                
                # Draw current ball position as a circle
                if recent_trajectory:
                    current_pos = (int(recent_trajectory[-1][0]), int(recent_trajectory[-1][1]))
                    cv2.circle(annotated_frame, current_pos, 5, (0, 0, 255), -1)  # Red dot
            
        # Draw ball detections with circles (yellow)
        if len(ball_detections_sv) > 0:
            # annotated_frame = circle_annotator.annotate(
            #     scene=annotated_frame,
            #     detections=ball_detections_sv
            # )
            annotated_frame = ball_label_annotator.annotate(
                scene=annotated_frame, 
                detections=ball_detections_sv,
                labels=["Ball"]
            )
        
        # Draw action detections with class-specific colors
        if len(action_detections_sv) > 0:
            # Group detections by class_id for color-specific annotation
            for class_id in np.unique(action_detections_sv.class_id):
                # Filter detections for this class
                class_mask = action_detections_sv.class_id == class_id
                class_detections = action_detections_sv[class_mask]
                
                # Get color for this class, default to RED if not found
                color = action_colors.get(class_id, sv.Color.RED)
                
                # Create annotator for this specific color
                class_box_annotator = sv.BoxAnnotator(thickness=2, color=color)
                
                # Annotate with class-specific color
                annotated_frame = class_box_annotator.annotate(
                    scene=annotated_frame, 
                    detections=class_detections
                )
                
                # Get labels for this class
                class_labels = [action_labels[i] for i, mask in enumerate(class_mask) if mask]
                annotated_frame = label_annotator.annotate(
                    scene=annotated_frame, 
                    detections=class_detections,
                    labels=class_labels
                )
        
        # Draw player detections with triangles (green)
        if len(player_detections_sv) > 0:
            annotated_frame = triangle_annotator.annotate(
                scene=annotated_frame, 
                detections=player_detections_sv
            )
        
        # Write frame to output video
        out.write(annotated_frame)
    
    # Cleanup
    cap.release()
    out.release()
    ml_manager.cleanup()
    
    print(f"Object detection completed (ball, actions, players). Output saved to: {output_path}")


def run_video_classification(video_path: str, output_path: str) -> None:
    """
    Run game state classification on video every 30 frames.
    
    This function:
    - Loads the ML Manager
    - Classifies game state every 30 frames
    - Visualizes classification results on the video
    - Saves the output video
    
    Args:
        video_path: Path to input video file
        output_path: Path to save output video with visualizations
    """
    print("Initializing ML Manager...")
    ml_manager = MLManager()
    
    # Check if game state classification model is available
    if not ml_manager.is_model_available('game_state_classification'):
        raise RuntimeError("Game state classification model not available")
    
    print("Opening video...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Classification parameters
    classification_interval = 30  # Classify every 30 frames
    frame_buffer = []
    current_game_state = "Unknown"
    current_confidence = 0.0
    
    print("Processing video frames...")
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processing frame {frame_count}/{total_frames}")
        
        # Add frame to buffer
        frame_buffer.append(frame.copy())
        
        # Keep only last 30 frames for classification
        if len(frame_buffer) > 30:
            frame_buffer = frame_buffer[-30:]
        
        # Classify game state every 30 frames
        if frame_count % classification_interval == 0 and len(frame_buffer) == 30:
            game_state_result = ml_manager.classify_game_state(frame_buffer)
            current_game_state = game_state_result.predicted_class
            current_confidence = game_state_result.confidence
            print(f"Frame {frame_count}: Game state = {current_game_state} (confidence: {current_confidence:.3f})")
        
        # Annotate frame with game state
        annotated_frame = frame.copy()
        
        # Draw game state information
        state_text = f"Game State: {current_game_state}"
        confidence_text = f"Confidence: {current_confidence:.3f}"
        frame_text = f"Frame: {frame_count}"
        
        # Position text in top-left corner
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        # Background rectangle for text
        text_size = cv2.getTextSize(state_text, font, font_scale, thickness)[0]
        cv2.rectangle(annotated_frame, (10, 10), (text_size[0] + 20, 100), (0, 0, 0), -1)
        cv2.rectangle(annotated_frame, (10, 10), (text_size[0] + 20, 100), (255, 255, 255), 2)
        
        # Draw text
        cv2.putText(annotated_frame, state_text, (15, 35), font, font_scale, (255, 255, 255), thickness)
        cv2.putText(annotated_frame, confidence_text, (15, 60), font, font_scale, (255, 255, 255), thickness)
        cv2.putText(annotated_frame, frame_text, (15, 85), font, font_scale, (255, 255, 255), thickness)
        
        # Color code the game state
        if current_game_state == "Play":
            color = (0, 255, 0)  # Green
        elif current_game_state == "No Play":
            color = (0, 0, 255)  # Red
        elif current_game_state == "Service":
            color = (255, 0, 255)  # Magenta
        else:
            color = (255, 255, 255)  # White
        
        # Draw colored border
        cv2.rectangle(annotated_frame, (10, 10), (text_size[0] + 20, 100), color, 3)
        
        # Write frame to output video
        out.write(annotated_frame)
    
    # Cleanup
    cap.release()
    out.release()
    ml_manager.cleanup()
    
    print(f"Video classification completed. Output saved to: {output_path}")


def main():
    """
    Example usage of the demo functions.
    """
    # Example video path (update with your actual video path)
    video_path = "../data/videos/Poland_Iran.mp4"
    output_detection = "../output/object_detection_demo.mp4"
    output_classification = "../output/video_classification_demo.mp4"
    
    # Create output directory if it doesn't exist
    Path("output").mkdir(exist_ok=True)
    
    print("Running object detection demo...")
    run_object_detection(video_path, output_detection)
    
    print("\nRunning video classification demo...")
    run_video_classification(video_path, output_classification)
    
    print("\nDemo completed successfully!")
    print(f"Object detection output: {output_detection}")
    print(f"Video classification output: {output_classification}")


if __name__ == "__main__":
    main()
