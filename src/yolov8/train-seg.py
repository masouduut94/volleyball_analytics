from ultralytics import YOLO

model = YOLO("../../models/yolov8s-seg.pt")

results = model.train(
        batch=32,
        device=[0],
        data="../../datasets/yaml_files/data-segment.yaml",
        epochs=200,
        imgsz=736,
    )

