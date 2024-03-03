from ultralytics import YOLO

model = YOLO("/home/masoud/Desktop/projects/volleyball_analytics/weights/yolov8m-seg.pt")

results = model.train(
    batch=32,
    device=[0],
    data="/home/masoud/Desktop/projects/volleyball_analytics/data/processed/court_segmentation/data.yaml",
    epochs=40,
    optimizer='AdamW',
    cos_lr=True,
    lr0=0.001,
    lrf=0.01,
    imgsz=640,
)
