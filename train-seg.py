from ultralytics import YOLO

model = YOLO("weights/yolov8n-seg.pt")

results = model.train(
        batch=32,
        device=[0],
        data="data/processed/data-segment.yaml",
        epochs=200,
        imgsz=1024,
    )

