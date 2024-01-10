from pathlib import Path

from ultralytics import YOLO
import cv2
from time import time
# from subprocess import call
"""
command:
$TRT = /home/masoud/TensorRT-8.6.1.6/bin/trtexec 
$TRT --onnx=/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.onnx --saveEngine=/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.trt

"""


if __name__ == '__main__':
    weights = '/home/masoud/Desktop/projects/volleyball_analytics/scripts/optimize/models/6_classes_half/best.pt'
    img_path = "/home/masoud/Desktop/projects/volleyball_analytics/data/inference_test/test"

    all_images = list(Path(img_path).glob('*.png'))
    base_path = Path(weights).parent
    trt_path = "/home/masoud/TensorRT-8.6.1.6/bin/trtexec"
    onnx_path = (base_path / (Path(weights).stem + '.onnx')).as_posix()
    save_path = (base_path / (Path(weights).stem + '.trt')).as_posix()

    model = YOLO(weights)
    formats = [
        'onnx',
        # 'trt',
        'openvino',
        'torchscript'
    ]

    for fmt in formats:
        # Export the model
        model.export(
            # batch=30,
            format=fmt,
            half=True,
        )

    # call(f'{trt_path} --onnx={onnx_path} --saveEngine={save_path}', shell=True)

    print("*"*40)
    print("*"*40)

    # weights = [w.as_posix() for w in base_path.glob('*')]
    imgs = [cv2.imread(img.as_posix()) for img in all_images]
    for w in weights:
        t1 = time()
        # print(w)
        for im in imgs:
            # im = cv2.resize(im, (640, 640))
            results = model.predict(
                im,
                # half=True,
                max_det=100,
                agnostic_nms=True,
                verbose=False
            )
        t2 = time()
        st1 = f"single img inference done: in {t2 - t1: .4f} seconds for {Path(w).name}"
        print(st1)
    print("*" * 40)
    print("*" * 40)

    # Batch inference results
    for fmt in formats:
        # Export the model
        model.export(
            batch=30,
            format=fmt,
            half=True
        )

    # call(f'{trt_path} --onnx={onnx_path} --saveEngine={save_path}', shell=True)
    print("*" * 40)
    print("*" * 40)

    weights = [w.as_posix() for w in base_path.glob('*')]
    for w in weights:
        t1 = time()
        results = model.predict(
                imgs,
                # half=True,
                device=0,
                max_det=100,
                agnostic_nms=True,
                verbose=False
            )
        t2 = time()

        st2 = f"batch inference (30 imgs) done. in {t2 - t1: .3f} seconds for {Path(w).name}"
        print(st2)
    print("*" * 40)
    print("*" * 40)
