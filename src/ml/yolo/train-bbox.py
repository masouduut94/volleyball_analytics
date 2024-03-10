"""
To know more about parameters:   https://docs.ultralytics.com/modes/train/#arguments

- epochs	100
- patience	50
- imgsz	640
- optimizer	'[SGD, Adam, Adamax, AdamW, NAdam, RAdam, RMSProp, auto]'
- cos_lr	False	use cosine learning rate scheduler
- close_mosaic	10	(int) disable mosaic augmentation for final epochs (0 to disable)
- label_smoothing	0.0
- amp	True	Automatic Mixed Precision (AMP) training, choices=[True, False]
- profile	False	profile ONNX and TensorRT speeds during training for loggers
- lr0	0.01	initial learning rate (i.e. SGD=1E-2, Adam=1E-3)
- lrf	0.01	final learning rate (lr0 * lrf)
- warmup_epochs	3.0	warmup epochs (fractions ok)
- warmup_momentum	0.8	warmup initial momentum
- nbs	64	nominal batch size
- plots	False	save plots and images during train/val


"""

from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.pt')  # load a pretrained.py model (recommended for training)
# https://docs.ultralytics.com/usage/cfg/#predict
# Batched Inference:
# https://medium.com/@smallerNdeeper/yolov8-batch-inference-implementation-using-tensorrt-2-converting-to-batch-model-engine-e02dc203fc8b

# Train the model with 1 GPU.
results = model.train(
    data='/home/masoud/Desktop/projects/volleyball_analytics/data/downloaded/roboflow_ball/data.yaml',
    epochs=100,
    task='detect',
    batch=32,
    # half=True,
    optimizer='AdamW',
    seed=1368,
    cos_lr=True,
    lr0=0.001,
    lrf=0.01,
    workers=16,
    imgsz=640,
    device=[0],
    plots=True
)
print(results)
