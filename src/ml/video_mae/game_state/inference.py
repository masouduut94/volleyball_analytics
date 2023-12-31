import cv2
from time import time
from tqdm import tqdm
from os import makedirs
from os.path import join
from pathlib import Path
from gamestate_detection import GameStateDetector

FPS = 30


def slice_video(serve_detection_model: GameStateDetector, video, output_path, buffer_size=30):
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


def annotate_service(serve_detection_model: GameStateDetector, video_path, output_path, buffer_size=30):
    video_path = Path(video_path)
    cap = cv2.VideoCapture(video_path.as_posix())
    assert video_path.is_file(), f'file {video_path.as_posix()} not found...'
    assert cap.isOpened(), f'the video file is not opening {video_path}'
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    buffer2 = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    pbar = tqdm(total=n_frames, desc=f'writing 0/{n_frames}')

    codec = cv2.VideoWriter_fourcc(*'mp4v')
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]
    filename = join(output_path, Path(video_path).stem + f'_visualization.mp4')
    writer = cv2.VideoWriter(filename, codec, fps, (w, h))
    t2 = 0
    t1 = 0
    while status:
        status, frame = cap.read()
        fno = int(cap.get(1))
        if not status:
            break
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pbar.update(1)
        buffer.append(frame)
        buffer2.append(fno)

        if len(buffer) != buffer_size:
            continue
        else:
            t1 = time()
            label = serve_detection_model.predict(buffer)
            t2 = time()
            pbar.set_description(f'processing {fno}/{n_frames} | p-time: {abs(t2 - t1): .3f}')

            match label:
                case 'service':
                    color = (0, 255, 0)
                case 'no-play':
                    color = (0, 0, 255)
                case 'play':
                    color = (255, 255, 0)
                case _:
                    color = (255, 255, 255)

            for f, fno in zip(buffer, buffer2):
                f = cv2.putText(
                    f, label, (w//2, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, color, 2
                )
                f = cv2.putText(
                    f, f"Frame # {fno}/{n_frames}", (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 0, 0), 2)
                writer.write(f)
        buffer.clear()
        buffer2.clear()

    writer.release()
    cap.release()
    pbar.close()


if __name__ == '__main__':
    # ckpt = "/home/masoud/Desktop/projects/volleyball_analytics/weights/game-status/services-650/checkpoint-3744"
    cfg = {
        'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/game-state/3-states/checkpoint-5424',
    }
    # ckpt = '/home/masoud/Desktop/projects/volleyball_analytics/weights/game-state/3-states/checkpoint-5424'
    model = GameStateDetector(cfg=cfg)
    video = '/media/HDD/datasets/VOLLEYBALL/RAW-VIDEOS/train/22.mp4'
    output_path = '/home/masoud/Desktop/projects/volleyball_analytics/runs/inference/game_state/output/triple_new_fp16'

    annotate_service(model, video, output_path, buffer_size=30)
