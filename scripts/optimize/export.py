"""
format	'torchscript'	format to export to
imgsz	640	image size as scalar or (h, w) list, i.e. (640, 480)
keras	False	use Keras for TF SavedModel export
optimize	False	TorchScript: optimize for mobile
half	False	FP16 quantization
int8	False	INT8 quantization
dynamic	False	ONNX/TensorRT: dynamic axes
simplify	False	ONNX/TensorRT: simplify model
opset	None	ONNX: opset version (optional, defaults to latest)
workspace	4	TensorRT: workspace size (GB)
nms	False	CoreML: add NMS

.torchscript => imgsz, optimize
onnx => imgsz, half, dynamic, simplify, opset
yolov8n_openvino_model/	=> imgsz, half, int8
.engine	=> imgsz, half, dynamic, simplify, workspace
coreml => yolov8n.mlpackage	✅	imgsz, half, int8, nms
saved_model	=> yolov8n_saved_model/	✅	imgsz, keras, int8
yolov8n.pb => imgsz
yolov8n.tflite => imgsz, half, int8
yolov8n_edgetpu.tflite => imgsz
tfjs | yolov8n_web_model/ => imgsz, half, int8
yolov8n_paddle_model/ => imgsz
yolov8n_ncnn_model/ => imgsz, half
"""

from ultralytics import YOLO

path = 'models/6_classes_half/best.pt'
# Load a model
model = YOLO(path)  # load an official model
# model = YOLO('path/to/best.pt')  # load a custom trained model

formats = [
    'onnx',
    # 'trt',
    'openvino',
    'torchscript'
]

# fmt = 'onnx'
# fmt = 'trt'
# fmt = 'openvino'
# fmt = 'torchscript'
for fmt in formats:
    # Export the model
    model.export(
        batch=30,
        format=fmt,
        half=True
    )
