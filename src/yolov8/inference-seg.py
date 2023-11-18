from ultralytics import YOLO
from tqdm import tqdm
import cv2
from pathlib import Path

# Load a model
weights = '/home/masoud/Desktop/projects/volleyball_analytics/src/yolov8/runs/segment/train/weights/best.pt'
input_path = "/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/test/videos"
output_path = '/home/masoud/Desktop/projects/volleyball_analytics/runs/inference'

model = YOLO(weights)  # load a custom model

for v in Path(input_path).glob('*.mp4'):
    video_path = v.as_posix()
    cap = cv2.VideoCapture(video_path)
    w, h, fps, _, n_frames = [int(cap.get(attrib)) for attrib in range(3, 8)]
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    output_file = Path(output_path) / f'{v.stem}_seg_output.mp4'

    writer = cv2.VideoWriter(
        output_file.as_posix(),
        codec,
        fps,
        (w, h)
    )

    total = int(cap.get(7))
    pbar = tqdm(total=total, desc='processing frames')

    # Loop through the video frames
    while cap.isOpened():
        pbar.update(1)
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            t = cv2.imread("/home/masoud/Desktop/projects/volleyball_analytics/test.png")
            # Run YOLOv8 inference on the frame
            results = model(t, verbose=False)
            # Visualize the results on the frame
            annotated_frame = results[0].plot()
            # Display the annotated frame
            writer.write(annotated_frame)
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    cap.release()
    writer.release()

cv2.destroyAllWindows()
