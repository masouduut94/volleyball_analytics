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
from rich.progress import Progress

from ml_manager.ml_manager import MLManager
from ml_manager.utils.tools import det2supervision, draw_trajectory

from vb_gui.calibration.database import CalibrationDB
from vb_gui.calibration.calibration_gui import create_gui


def run_object_detection(ml_manager: MLManager,
                         video_path: str,
                         output_path: str,
                         court_calibration_json: dict) -> None:
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
        court_calibration_json:
        ml_manager: The MLManager instance.
        video_path: Path to input video file.
        output_path: Path to save output video with visualizations
    """
    print("Initializing ML Manager...")

    ml_manager.check_models()

    print("Opening video...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Get video properties
    width, height, fps, _, total_frames = [int(cap.get(prop)) for prop in range(3, 8)]
    print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")

    # setup output folder
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Initialize supervision annotators
    ball_annotator = sv.LabelAnnotator(color=sv.Color.YELLOW, text_thickness=1, text_scale=0.5)
    label_annotator = sv.LabelAnnotator(text_thickness=1, text_scale=0.5)
    # Players annotators
    triangle_annotator = sv.TriangleAnnotator(color=sv.Color.GREEN)
    # ellipse_annotator = sv.EllipseAnnotator(color=sv.Color.GREEN)

    # Define colors for different action classes (class_id -> color)
    COLORS = {
        "ball": sv.Color.RED,
        "block": sv.Color.BLUE,
        "receive": sv.Color.from_hex('#800080'),
        "set": sv.Color.from_hex("#FFA500"),
        "spike": sv.Color.from_hex("#FFC0CB")
    }

    # Tracking state
    tracker = sv.ByteTrack()
    ball_trajectory = []
    frame_count = 0
    print("Processing video frames...")

    with Progress() as progress:
        task = progress.add_task(
            "[green]Processing video...",
            total=total_frames
        )

        while frame_count < total_frames:
            ret, frame = cap.read()
            progress.update(task, advance=1)

            if not ret:
                progress.update(task, advance=30)
                break

            frame_count += 1
            # Detect all objects (actions, ball, players) using detect_all
            actions, ball, players = ml_manager.detect_all(
                frame,
                conf_threshold=0.25,
                iou_threshold=0.45
            )

            # Annotate frame
            annotated_frame = frame.copy()

            # Process ball detections
            if ball:
                ball_detections_sv = ball.to_supervision()
                annotated_frame = ball_annotator.annotate(
                    scene=annotated_frame,
                    detections=ball_detections_sv,
                    labels=["ball"]
                )
                # Update ball trajectory for tracking
                ball_trajectory.append(ball.bbox.center)

            court = court_calibration_json["court_corners"]
            # TODO: Filter players outside court
            # ml_manager.filter_people_outside_court(players, court)

            # Process action detections
            action_detections_sv = det2supervision(detections=actions)

            # Process player detections
            player_detections_sv = det2supervision(detections=players, tracking_instance=tracker)

            # Draw ball trajectory (8 frames trailing)
            if ball_trajectory:
                draw_trajectory(annotated_frame, ball_trajectory, 12)


            # Draw action detections with class-specific colors
            if len(action_detections_sv) > 0:
                # Group detections by class_id for color-specific annotation
                for class_id in np.unique(action_detections_sv.class_id):
                    # Filter detections for this class
                    class_mask = action_detections_sv.class_id == class_id
                    class_detections: sv.Detections = action_detections_sv[class_mask]

                    # Get color for this class, default to RED if not found
                    action = ml_manager.action_detector.yolo_module.id2class(class_id)
                    color = COLORS.get(action, sv.Color.WHITE)

                    # Create annotator for this specific color
                    class_box_annotator = sv.BoxAnnotator(thickness=2, color=color)

                    # Annotate with class-specific color
                    annotated_frame = class_box_annotator.annotate(
                        scene=annotated_frame,
                        detections=class_detections
                    )

                    # Get labels for this class
                    class_labels = [
                        ml_manager.action_detector.action_id2name(det)
                        for det in class_detections.class_id
                    ]
                    # class_labels = [action_labels[i] for i, mask in enumerate(class_mask) if mask]
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
                labels = [
                    f"Player #{tracker_id}"
                    for tracker_id in player_detections_sv.tracker_id
                ]
                annotated_frame = label_annotator.annotate(
                    scene=annotated_frame,
                    detections=player_detections_sv,
                    labels=labels
                )

            # Write frame to output video
            out.write(annotated_frame)

        # Cleanup
        cap.release()
        out.release()

        print(f"Object detection completed (ball, actions, players). Output saved to: {output_path}")


def run_video_classification(ml_manager: MLManager, video_path: str, output_path: str) -> None:
    """
    Run game state classification on video every 30 frames.

    This function:
    - Loads the ML Manager
    - Classifies game state every 30 frames
    - Visualizes classification results on the video
    - Saves the output video

    Args:
        ml_manager: Model Manager that loads and manages models.
        video_path: Path to input video file
        output_path: Path to save output video with visualizations
    """
    print("Initializing ML Manager...")

    # Check if game state classification model is available
    if not ml_manager.is_model_available('game_state_classification'):
        raise RuntimeError("Game state classification model not available")

    print("Opening video...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Get video properties
    width, height, fps, _, total_frames = [int(cap.get(prop)) for prop in range(3, 8)]
    print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")

    # setup output folder
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Classification parameters
    frame_buffer = []
    current_confidence = 0.0

    print("Processing video frames...")
    frame_count = 0

    with Progress() as progress:
        task = progress.add_task(
            "[green]Processing video...",
            total=total_frames
        )

        while True:
            ret, frame = cap.read()
            frame_count += 1
            progress.update(task, advance=1)

            if not ret:
                progress.update(task, advance=30)
                break

            # Add frame to buffer
            frame_buffer.append(frame.copy())

            if len(frame_buffer) != 30:
                continue

            # Classify game state every 30 frames
            game_state_result = ml_manager.classify_game_state(frame_buffer)

            current_game_state = game_state_result.predicted_class
            current_confidence = game_state_result.confidence

            progress.update(
                task,
                description=(
                    f"[green]Frame {frame_count} | "
                    f"State: {current_game_state} | "
                    f"Conf: {current_confidence:.3f}"
                )
            )

            # Annotate frame with game state
            annotated_frame = frame.copy()

            state_text = f"Game State: {current_game_state}"
            confidence_text = f"Confidence: {current_confidence:.3f}"
            frame_text = f"Frame: {frame_count}"

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2

            text_size = cv2.getTextSize(state_text, font, font_scale, thickness)[0]

            cv2.rectangle(annotated_frame, (10, 10), (text_size[0] + 20, 100), (0, 0, 0), -1)

            cv2.rectangle(annotated_frame, (10, 10), (text_size[0] + 20, 100), (255, 255, 255), 2)

            cv2.putText(annotated_frame, state_text, (15, 35), font, font_scale, (255, 255, 255), thickness)

            cv2.putText(annotated_frame, confidence_text, (15, 60), font, font_scale, (255, 255, 255), thickness)

            cv2.putText(annotated_frame, frame_text, (15, 85), font, font_scale, (255, 255, 255), thickness)

            if current_game_state == "Play":
                color = (0, 255, 0)
            elif current_game_state == "No Play":
                color = (0, 0, 255)
            elif current_game_state == "Service":
                color = (255, 0, 255)
            else:
                color = (255, 255, 255)

            cv2.rectangle(annotated_frame, (10, 10), (text_size[0] + 20, 100), color, 3)

            out.write(annotated_frame)

    # Cleanup
    cap.release()
    out.release()
    ml_manager.cleanup()

    print(f"Video classification completed. Output saved to: {output_path}")


def main():
    # TODO:
    #  Design the software based on this: https://chatgpt.com/share/6a6deeb9-ba74-83eb-8290-3a2afbf184f4
    #  Inference:
    #  1. Add supervision tracker to players.
    #  2. Add Heatmap for each player later.
    #  3. Check if there are better and easier to work with 'trackers'.
    #  4. Add court detection to the pipeline and filter the persons outside court.
    #  5. Add integration of video classification and object detection together and API endpoints in
    #     the inference.
    #  6. Update the GIFs and videos on the readme file with the new demos.
    #  7. After the video classification has created the slice, add it to a job queue and process the
    #     slices with object detection.
    #  8. 2D visualization of the court and the ball bounce points.
    #  Front-end:
    #  1. Page 1: Inference page -> Object detection and Video slicing
    #  2. Page 2: Annotation tool -> Being able to annotate and use the models to help out.
    #  3. Page 3: Set the court corners and the 1/3rd line. In order to omit the court detection lines.
    #  4. Page 4: Analysis page -> Shows the court on 2d (or maybe 3d) and plots ball, players locations on the court.
    """
    Example usage of the demo functions.
    """
    # Example video path (update with your actual video path)
    root_path = Path().cwd().parent
    db_path = root_path.joinpath("db").joinpath('calibration.db').as_posix()
    ml_manager = MLManager()
    # output_classification = "../output/IRN_vs_FRA_video_classification.mp4"


    # Calibration of the video for court points.
    db = CalibrationDB(db_path=db_path)

    # Select video using the GUI.
    result_json, video_path = create_gui(
        video_path=None,
        db_instance=db,
    )

    output_detection = root_path.joinpath("output").joinpath(video_path.stem + '_object_detection.mp4').as_posix()

    #
    # Create output directory if it doesn't exist
    Path("output").mkdir(exist_ok=True)

    print("Running object detection demo...")
    run_object_detection(ml_manager, video_path, output_detection, result_json)

    # print("\nRunning video classification demo...")
    # run_video_classification(ml_manager, video_path, output_classification)

    print("\nDemo completed successfully!")
    print(f"Object detection output: {output_detection}")
    # print(f"Video classification output: {output_classification}")


if __name__ == "__main__":
    main()
