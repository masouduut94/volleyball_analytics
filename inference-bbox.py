import cv2
from ultralytics import YOLO

# https://docs.ultralytics.com/modes/predict/#plotting-results

# Load a pretrained YOLOv8n model
model_path = '/home/masoud/Desktop/projects/volleyball_analytics/runs/detect/train0/weights/best.pt'

# Load the YOLOv8 model
model = YOLO(model_path)

# Open the video file
video_path = '/home/masoud/Desktop/projects/volleyball_analytics/videos/7.mp4'
cap = cv2.VideoCapture(video_path)

w, h, fps = [int(cap.get(i)) for i in range(3, 6)]

writer = cv2.VideoWriter(
	'output.mp4', 
	cv2.VideoWriter_fourcc(*'mp4v'), 
	fps, 
	(w, h)
)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        results = model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        writer.write(annotated_frame) 

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
