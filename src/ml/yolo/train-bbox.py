from ultralytics import YOLO

# Load a model
model = YOLO('/home/masoud/Desktop/projects/volleyball_analytics/weights/yolov8n.pt')  # load a pretrained.py model (recommended for training)

# Train the model with 1 GPU.
results = model.train(
    data='/home/masoud/Desktop/projects/volleyball_analytics/data/processed/action_detection/data.yaml',
    epochs=200,
    batch=16,
    imgsz=640,
    device=[0]
)
