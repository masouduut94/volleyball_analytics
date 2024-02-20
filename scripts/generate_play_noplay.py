import cv2
import random
import numpy as np
import pandas as pd
from tqdm import tqdm
from os import makedirs
from pathlib import Path
from natsort import natsorted
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

plt.rcParams['figure.figsize'] = [15, 10]

data_path = '/home/masoud/Desktop/C'
video_path = Path(data_path) / 'train'
annotation_path = Path(data_path) / 'game-status'

annotations = natsorted(list(annotation_path.glob('*.xml')), key=lambda x: x.stem)
videos = natsorted(list(video_path.glob('*')), key=lambda x: x.stem)
videos = [vid for vid in videos if vid.stem in [annot.stem for annot in annotations]]

pairs = list(zip(videos, annotations))


def get_label(annots, label_name):
    return [f.get('name') for f in annots if f.find('tag').get('label') == label_name]


def get_frame_nos(annot_path, label='serving-start'):
    # Parse file
    data = ET.parse(annot_path)
    # Separate all images tags
    images = data.findall('image')
    # Filter the images with no image_tag
    images = [img for img in images if img.find('tag') is not None]
    # Get the image frame number of the ones that matches the label given like `serving-start`, ....
    frame_str = get_label(images, label)
    frame_nos = [int(f.split('_')[1]) for f in frame_str]
    return frame_nos


def random_start_frame(st, end, divisions=5, vdo_length=50):
    arr = np.arange(st, end - vdo_length, dtype=np.int32)
    arrays = np.array_split(arr, divisions)
    results = [random.choice(r.tolist()) for r in arrays]
    return results


output_base_dir = '/home/masoud/Desktop/projects/volleyball_analytics/data/preprocessed/game-state-2-classes'
game_dir = Path(output_base_dir) / 'play'
no_game_dir = Path(output_base_dir) / 'no-play'
makedirs(game_dir.as_posix(), exist_ok=True)
makedirs(no_game_dir.as_posix(), exist_ok=True)
vdo_length = 30


def write_video(cap: cv2.VideoCapture, st: int, fps: int, width: int, height: int,
                video_length: int, output_path: Path, video: Path, label: str):
    cap.set(1, st)
    filename = f'{label}_{video.stem}_st1_{st}_end_{st + video_length}.mp4'
    output_file = (output_path / filename).as_posix()
    writer = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )
    for i in range(video_length):
        status, frame = cap.read()
        if status:
            writer.write(frame)

    writer.release()


for video, annot in pairs:
    cap = cv2.VideoCapture(video.as_posix())
    w, h, fps = [int(cap.get(i)) for i in range(3, 6)]

    serves = get_frame_nos(annot, 'serving-start')
    end_serves = get_frame_nos(annot, 'serving-end')
    end_games = get_frame_nos(annot, 'in-game-end')

    data = {
        'serve': serves, 'end_serve': end_serves, 'end_game': end_games
    }
    df = pd.DataFrame(data=data)

    df['next_serve'] = None

    for i in range(len(df)):
        if i != len(df) - 1:
            next_serve = df.at[i + 1, 'serve']
            df.at[i, 'next_serve'] = next_serve
        else:
            df.at[i, 'next_serve'] = None

    pbar = tqdm(total=len(df))
    pbar.set_description(f"Processing {video.name}")
    for i, row in df.iterrows():
        pbar.update(1)
        start_inplay_fno = row['serve']
        end_inplay_fno = start_noplay_fno = row['end_game']
        end_noplay_fno = row['next_serve']
        #  ####################### Generate in-play videos #################################
        pbar.set_description(f"1/2: {video.name} generating in-play videos")
        length = end_inplay_fno - start_inplay_fno
        if length < (vdo_length + 5):
            continue
        elif (vdo_length+5) <= length <= 120:
            # Generate 1 video.
            st = random_start_frame(start_inplay_fno, end_inplay_fno, divisions=1, vdo_length=vdo_length)
            write_video(
                cap=cap,
                st=st[0],
                fps=fps,
                width=w,
                height=h,
                video_length=vdo_length,
                output_path=game_dir,
                video=video,
                label='inplay'
            )

        elif 120 < length <= 300:
            start_frames = random_start_frame(start_inplay_fno, end_inplay_fno, divisions=4, vdo_length=vdo_length)
            for f in start_frames:
                write_video(
                    cap=cap,
                    st=f,
                    fps=fps,
                    width=w,
                    height=h,
                    video_length=vdo_length,
                    output_path=game_dir,
                    video=video,
                    label='inplay'
                )

        elif length >= 300:
            st = start_inplay_fno
            end = end_inplay_fno

            start_frames = random_start_frame(st, end, divisions=(length//vdo_length) - 1, vdo_length=vdo_length)
            for f in start_frames:
                write_video(
                    cap=cap,
                    st=f,
                    fps=fps,
                    width=w,
                    height=h,
                    video_length=vdo_length,
                    output_path=game_dir,
                    video=video,
                    label='inplay'
                )

        #  ######################## Generate no-play videos #################################
        pbar.set_description(f"2/2: {video.name} generating no-play videos")

        if end_noplay_fno is None or start_noplay_fno is None:
            continue
        length = end_noplay_fno - start_noplay_fno

        if length < vdo_length + 5:
            continue

        elif (vdo_length + 5) <= length <= 120:
            # Generate 1 video.
            st = random_start_frame(
                start_noplay_fno, end_noplay_fno, divisions=1, vdo_length=vdo_length
            )
            write_video(
                cap=cap,
                st=st[0],
                fps=fps,
                width=w,
                height=h,
                video_length=vdo_length,
                output_path=no_game_dir,
                video=video,
                label='noplay'
            )

        elif 120 < length <= 300:
            start_frames = random_start_frame(
                start_noplay_fno, end_noplay_fno, divisions=4, vdo_length=vdo_length
            )
            for f in start_frames:
                write_video(
                    cap=cap,
                    st=f,
                    fps=fps,
                    width=w,
                    height=h,
                    video_length=vdo_length,
                    output_path=no_game_dir,
                    video=video,
                    label='noplay'
                )

        elif length > 500:
            start_frames = random_start_frame(
                start_noplay_fno, end_noplay_fno, divisions=(length//vdo_length) - 1, vdo_length=vdo_length
            )
            for f in start_frames:
                write_video(
                    cap=cap,
                    st=f,
                    fps=fps,
                    width=w,
                    height=h,
                    video_length=vdo_length,
                    output_path=no_game_dir,
                    video=video,
                    label='noplay'
                )
    pbar.close()



