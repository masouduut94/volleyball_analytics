from pathlib import Path
from typing import List

import cv2
from tqdm import tqdm
from ultralytics import YOLO
from numpy.typing import NDArray
from src.utilities.utils import BoundingBox, Meta

# weights = '/home/masoud/Desktop/projects/volleyball_analytics/weights/ball_segment/model2/weights/best.pt'

__all__ = ['BallSegmentor']


class BallSegmentor:
    def __init__(self, cfg: dict):
        self.model = YOLO(cfg['weight'])
        self.labels = cfg['labels']

    def predict(self, inputs: NDArray) -> List[BoundingBox]:
        outputs = self.model(inputs, verbose=False)
        confs = outputs[0].boxes.conf.cpu().detach().numpy().tolist()
        boxes = outputs[0].boxes.xyxy.cpu().detach().numpy().tolist()

        results: List[BoundingBox] = []
        for box, conf in zip(boxes, confs):
            # TODO: make it suitable for multi-class yolo.
            b = BoundingBox(box, name='ball', conf=float(conf))
            results.append(b)
        results.sort(key=lambda x: (x.conf, x.area), reverse=True)
        return results

    def batch_predict(self, inputs: List[NDArray]) -> List[List[BoundingBox]]:
        outputs = self.model(inputs, verbose=False)
        results = []
        for res in outputs:
            confs = res.boxes.conf.cpu().detach().numpy().tolist()
            boxes = res.boxes.xyxy.cpu().detach().numpy().tolist()

            detections: List[BoundingBox] = []
            for box, conf in zip(boxes, confs):
                b = BoundingBox(box, name='ball', conf=float(conf))
                detections.append(b)
            detections.sort(key=lambda x: (x.conf, x.area), reverse=True)
            results.append(detections)
        return results

    @staticmethod
    def draw(frame: NDArray, bboxes: List[BoundingBox], use_ellipse: bool = False, use_marker=False, color=Meta.green,
             use_bbox=True, use_title: bool = True):
        for bb in bboxes:
            if use_marker:
                frame = bb.draw_marker(frame, color)
            if use_ellipse:
                frame = bb.draw_ellipse(frame, color)
            if use_bbox:
                frame = bb.plot(frame, color, title=bb.name if use_title else '')
        return frame


if __name__ == '__main__':
    video = 'C:/Users/masoud/Desktop/Projects/volleyball_analytics/data/raw/videos/test4'
    output = 'C:/Users/masoud/Desktop/Projects/volleyball_analytics/run/inference'
    cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/ball_segment/model2/weights/best.pt',
        "labels": {0: 'ball'}
    }

    action_detector = BallSegmentor(cfg=cfg)
    cap = cv2.VideoCapture(video)
    assert cap.isOpened()

    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_file = Path(video) / (Path(video).stem + 'ball_detection_output.mp4')
    writer = cv2.VideoWriter(output_file.as_posix(), fourcc, fps, (w, h))

    for fno in tqdm(list(range(n_frames))):
        cap.set(1, fno)
        status, frame = cap.read()
        bboxes = action_detector.predict(frame)
        frame = action_detector.draw(frame, bboxes)
        writer.write(frame)

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f'saved results in {output_file}')
