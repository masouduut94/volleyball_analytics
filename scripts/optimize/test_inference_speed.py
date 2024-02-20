from pathlib import Path

from ultralytics import YOLO
import cv2
from time import time
"""
command:
$TRT = /home/masoud/TensorRT-8.6.1.6/bin/trtexec 
$TRT --onnx=/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.onnx --saveEngine=/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.trt

"""


if __name__ == '__main__':
    weights = '/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.engine'
    img_path = "/home/masoud/Desktop/projects/volleyball_analytics/data/inference_test/test"
    single_mode = True

    all_images = list(Path(img_path).glob('*.png'))
    imgs = [cv2.imread(img.as_posix()) for img in all_images]
    base_path = Path(weights).parent
    model = YOLO(weights)

    args = {}
    w = Path(weights)
    if w.name.endswith('torchscript'):
        args = dict(half=False, agnostic_nms=True, max_det=300, verbose=False)
    if w.name.endswith('pt'):
        args = dict(half=False, agnostic_nms=False, max_det=300, verbose=True)
    if w.name.endswith('openvino_model'):
        args = dict(half=True, agnostic_nms=True, max_det=300, verbose=False)
    if w.name.endswith('onnx'):
        args = dict(half=False, agnostic_nms=True, max_det=300, verbose=False)
    model = YOLO(model=w, task='detect')

    if single_mode:
        for im in imgs:
            # t1 = time()
            results = model(
                source=im,
                **args
            )
        #     t2 = time()
        #     st1 = f"single img inference: {t2 - t1: .4f} seconds for {Path(w).name}"
        #     print(st1)
        # print("*" * 40)
        # print("*" * 40)

    else:
        t1 = time()
        results = model(
            source=imgs,
            **args
        )
        t2 = time()
        st1 = f"batch inference: {t2 - t1: .4f} seconds for {Path(w).name}"
        print(st1)
        print("*" * 40)
        print("*" * 40)



"""
==========================================================================================================
==========================================================================================================
pytorch model | half

0: 384x640 1 ball, 2 blocks, 1 spike, 39.2ms
Speed: 2.5ms preprocess, 39.2ms inference, 159.5ms postprocess per image at shape (1, 3, 384, 640)

0: 384x640 1 serve, 1.8ms
Speed: 0.9ms preprocess, 1.8ms inference, 0.7ms postprocess per image at shape (1, 3, 384, 640)

0: 384x640 1 receive, 1.6ms
Speed: 0.8ms preprocess, 1.6ms inference, 0.4ms postprocess per image at shape (1, 3, 384, 640)
==========================================================================================================
==========================================================================================================

int8 | 

0: 384x640 1 ball, 2 blocks, 1 spike, 39.3ms
Speed: 2.7ms preprocess, 39.3ms inference, 163.4ms postprocess per image at shape (1, 3, 384, 640)

0: 384x640 1 serve, 1.9ms
Speed: 0.9ms preprocess, 1.9ms inference, 0.7ms postprocess per image at shape (1, 3, 384, 640)

0: 384x640 1 receive, 1.6ms
Speed: 0.9ms preprocess, 1.6ms inference, 0.4ms postprocess per image at shape (1, 3, 384, 640)



"""