from ultralytics import YOLO

# Load a model
model = YOLO('yolov8s.pt')  # load a pretrained model (recommended for training)

# Train the model with 2 GPUs
results = model.train(data='data.yaml', epochs=100, imgsz=640, device=[0])
