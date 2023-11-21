from ultralytics import YOLO

# Load a model
model = YOLO('./models/yolov8n.pt')  # load a pretrained.py model (recommended for training)

# Train the model with 1 GPU.
results = model.train(
    data='datasets/data.yaml',
    epochs=200,
    batch=16,
    imgsz=1000,
    device=[0]
)
