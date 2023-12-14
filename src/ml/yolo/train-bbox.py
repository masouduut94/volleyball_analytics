from ultralytics import YOLO

# Load a model
model = YOLO('/home/masoud/Desktop/projects/volleyball_analytics/weights/yolov8s.pt')  # load a pretrained.py model (recommended for training)
# https://docs.ultralytics.com/usage/cfg/#predict
# Batched Inference:
# https://medium.com/@smallerNdeeper/yolov8-batch-inference-implementation-using-tensorrt-2-converting-to-batch-model-engine-e02dc203fc8b

# Train the model with 1 GPU.
results = model.train(
    data='/home/masoud/Desktop/projects/volleyball_analytics/data/processed/vb_actions_5.yaml',
    epochs=200,
    task='detect',
    batch=32,
    # optimizer='AdamW',
    seed=1368,
    cos_lr=True,
    lrf=0.1,
    lr0=0.0001,
    workers=16,
    imgsz=640,
    device=[0]
)
