from ultralytics import YOLO

# Load a model
model = YOLO('/home/masoud/Desktop/projects/volleyball_analytics/weights/yolov8n.pt')  # load a pretrained.py model (recommended for training)

# Train the model with 1 GPU.
results = model.train(
    data='/home/masoud/Desktop/projects/volleyball_analytics/data/processed/vb_actions_6.yaml',
    epochs=200,
    batch=32,
    imgsz=640,
    half=True,
    device=[0]
)
