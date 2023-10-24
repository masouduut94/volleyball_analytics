from ultralytics import YOLO
from tqdm import tqdm
import cv2

# Load a model
weights = '/home/masoud/Desktop/projects/volleyball_analytics/runs/segment/train2/weights/best.pt'
video_path = '/home/masoud/Desktop/projects/volleyball_analytics/videos/7.mp4'

model = YOLO(weights)  # load a custom model
cap = cv2.VideoCapture(video_path)
w, h, fps, _, n_frames = [int(cap.get(attrib)) for attrib in range(3, 8)]
codec = cv2.VideoWriter_fourcc(*'mp4v')

writer = cv2.VideoWriter('output_seg.mp4', codec, fps, (w, h))

print(w," ", h, " ", fps," ", n_frames)
for frame_num in tqdm(list(range(n_frames))):
    cap.set(1, frame_num)
    status, frame = cap.read()
    results = model(frame)
    output_frame = results[0].plot()

    # Display the annotated frame
    writer.write(output_frame)
    if frame_num == 4000:
        break


writer.release()
cap.release()
cv2.destroyAllWindows()
# # Predict with the model
# results = model('https://ultralytics.com/images/bus.jpg')  # predict on an image



