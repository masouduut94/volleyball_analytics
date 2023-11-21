from pretrained import ServeDetectionModel
import cv2
import numpy as np
import pandas as pd
import time
from os import makedirs
from tqdm import tqdm
from os.path import join
from pathlib import Path

FPS = 30


def slice_video(serve_detection_model: ServeDetectionModel, video, output_path, buffer_size=30):
    cap = cv2.VideoCapture(video)
    assert cap.isOpened(), f'the video file is not opening {video}'
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    id_buffer = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    pbar = tqdm(total=n_frames, desc='processing rally #1')
    serves_index_buffer = []
    rally_counter = 0

    codec = cv2.VideoWriter_fourcc(*'mp4v')
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
    filename = join(output_path, Path(video).stem + f'_visualization.mp4')
    writer = cv2.VideoWriter(filename, codec, fps, (w, h))

    while status:
        status, frame = cap.read()
        if not status:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pbar.update(1)
        frame_id = int(cap.get(1))
        buffer.append(frame)
        id_buffer.append(frame_id)

        if len(buffer) != buffer_size:
            continue

        label = serve_detection_model.predict(buffer)
        if label == 'serve':
            start_frame_id = id_buffer[0]
            serves_index_buffer.append(start_frame_id)
            rally_counter += 1
            pbar.set_description(f'processing rally #{rally_counter}')
        id_buffer.clear()
        buffer.clear()

    pbar.close()

    # When we have the start and end frame indexes, we start writing the video slices.
    for i, _ in enumerate(tqdm(serves_index_buffer[:-1], desc='writing videos')):
        start = serves_index_buffer[i]
        end = serves_index_buffer[i + 1]

        codec = cv2.VideoWriter_fourcc(*'mp4v')
        w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
        filename = join(output_path, Path(video).stem + f'{start}_{end}.mp4')
        writer = cv2.VideoWriter(filename, codec, fps, (w, h))
        # cap.set(1, start)
        for i in range(start, end):
            cap.set(1, i)
            status, frame = cap.read()
            writer.write(frame)
        writer.release()


def annotate_service(serve_detection_model: ServeDetectionModel, video, output_path, buffer_size=30):
    cap = cv2.VideoCapture(video)
    assert cap.isOpened(), f'the video file is not opening {video}'
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    pbar = tqdm(total=n_frames, desc='writing frames')
    rally_counter = 0

    codec = cv2.VideoWriter_fourcc(*'mp4v')
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
    filename = join(output_path, Path(video).stem + f'_visualization.mp4')
    writer = cv2.VideoWriter(filename, codec, fps, (w, h))

    while status:
        status, frame = cap.read()
        if not status:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pbar.update(1)
        frame_id = int(cap.get(1))
        buffer.append(frame)

        if len(buffer) != buffer_size:
            continue

        label = serve_detection_model.predict(buffer)
        for f in buffer:
            f = cv2.putText(
                f, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2
            )
            writer.write(f)
        buffer.clear()

    pbar.close()
    writer.release()


if __name__ == '__main__':
    ckpt = "/mnt/disk1/projects/table_tennis/masoud/TT/rally_detection/video_mae/serve_detection_flipped_ckpt/checkpoint-3066"
    model = ServeDetectionModel(ckpt=ckpt)
    video_path = '/mnt/disk1/projects/table_tennis/masoud/TT/videos/test_videos/rally5.mp4'
    output_path = '/mnt/disk1/projects/table_tennis/masoud/TT/rally_detection/video_mae/sliced_videos'

    annotate_service(model, video_path, output_path, buffer_size=20)