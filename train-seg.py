from ultralytics import YOLO

model = YOLO("yolov8n-seg.pt")

results = model.train(
        batch=2,
        device='cpu',
        data="datasets/yaml_files/data-segment.yaml",
        epochs=100,
        imgsz=720,
    )

