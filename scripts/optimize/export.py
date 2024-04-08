"""
$TRT --onnx= --saveEngine=/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.trt
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

if __name__ == '__main__':
    path = 'models/6_classes_half/best.pt'
    model = YOLO(path)
    single_mode = True
    # fmt = 'trt'
    # fmt = 'onnx'
    # fmt = 'openvino'
    fmt = 'torchscript'

    args = {}
    if fmt == 'onnx':
        args = dict(format=fmt, simplify=False, half=False, dynamic=False)
    elif fmt == 'torchscript':
        args = dict(format=fmt, optimize=False)
    elif fmt == 'openvino':
        args = dict(format=fmt, half=False, int8=False)
    if single_mode:
        model.export(
            **args
        )
    else:
        args['batch'] = 30
        model.export(
            # batch=30,
            **args
        )
