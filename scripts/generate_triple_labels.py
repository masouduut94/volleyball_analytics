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
from os.path import join
from random import shuffle
from shutil import copy2, move

plt.rcParams['figure.figsize'] = [15, 10]

data_path = '/home/masoud/Desktop/C'
video_path = Path(data_path) / 'train'
annotation_path = Path(data_path) / 'game-status'

annotations = natsorted(list(annotation_path.glob('*.xml')), key=lambda x: x.stem)
videos = natsorted(list(video_path.glob('*')), key=lambda x: x.stem)
videos = [vid for vid in videos if vid.stem in [annot.stem for annot in annotations]]
pairs = list(zip(videos, annotations))

get_label = lambda annots, label_name: [f.get('name') for f in annots if f.find('tag').get('label') == label_name]


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


def write_video(cap: cv2.VideoCapture, st: int, fps: int, width: int, height: int,
                video_length: int, output_path: Path, video: Path, label: str, augment_LR=True):
    cap.set(1, st)
    filename = f'{label}_{video.stem}_st_{st}_end_{st + video_length}'
    output_file = (output_path / (filename + '.mp4')).as_posix()
    output_file_LR = (output_path / (filename + '_flipped_LR.mp4')).as_posix()

    writer = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )
    if augment_LR:
        writer2 = cv2.VideoWriter(
            output_file_LR,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

    for i in range(video_length):
        status, frame = cap.read()
        if status:
            writer.write(frame)
            if augment_LR:
                transformed = frame[:, ::-1]
                writer2.write(transformed)
    writer.release()
    writer2.release()


if __name__ == '__main__':
    output_base_dir = '/home/masoud/Desktop/projects/volleyball_analytics/data/preprocessed/game-state'
    game_dir = Path(output_base_dir) / 'play'
    no_game_dir = Path(output_base_dir) / 'no-play'
    service_dir = Path(output_base_dir) / 'service'
    makedirs(game_dir.as_posix(), exist_ok=True)
    makedirs(no_game_dir.as_posix(), exist_ok=True)
    makedirs(service_dir.as_posix(), exist_ok=True)
    vdo_length = 30
    serve_counter = 0
    inplay_counter = 0
    noplay_counter = 0

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
            pbar.set_description(
                f"Process {video.name} => | no_play: {noplay_counter} | in_play: {inplay_counter} | service {serve_counter} |"
            )
            pbar.update(1)
            start_serve_fno = row['serve']
            end_serve_fno = start_inplay_fno = row['end_serve']
            end_inplay_fno = start_noplay_fno = row['end_game']
            end_noplay_fno = row['next_serve']

            #  ####################### Generate service videos #################################
            length = end_serve_fno - start_serve_fno
            cap.set(1, start_serve_fno)

            if length < 30:
                continue
            elif length >= 30:
                write_video(
                    cap=cap,
                    st=start_serve_fno,
                    fps=fps,
                    width=w,
                    height=h,
                    video_length=vdo_length,
                    output_path=service_dir,
                    video=video,
                    label='service'
                )

                write_video(
                    cap=cap,
                    st=end_serve_fno-30,
                    fps=fps,
                    width=w,
                    height=h,
                    video_length=vdo_length,
                    output_path=service_dir,
                    video=video,
                    label='service'
                )
                serve_counter += 4  # if LR augment is on

            #  ####################### Generate in-play videos #################################
            length = end_inplay_fno - start_inplay_fno
            if length < (vdo_length + 5):
                continue
            elif (vdo_length + 5) <= length <= 120:
                # Generate 1 video.
                st = random_start_frame(
                    start_inplay_fno, end_inplay_fno, divisions=1, vdo_length=vdo_length
                )
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
                inplay_counter += 2
            elif 120 < length <= 300:
                start_frames = random_start_frame(
                    start_inplay_fno, end_inplay_fno, divisions=4, vdo_length=vdo_length
                )
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
                    inplay_counter += 2

            elif length >= 300:
                st = start_inplay_fno
                end = end_inplay_fno

                start_frames = random_start_frame(
                    st, end, divisions=(length // vdo_length) - 1, vdo_length=vdo_length
                )
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
                    inplay_counter += 2

            #  ######################## Generate no-play videos #################################

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
                noplay_counter += 2

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
                    noplay_counter += 2

            elif length > 500:
                start_frames = random_start_frame(
                    start_noplay_fno, end_noplay_fno, divisions=(length // vdo_length) - 1, vdo_length=vdo_length
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
                    noplay_counter += 2

        pbar.close()

    print("finished data generation ....")
    # Split to train-test
    # dataset_root = '/home/masoud/Desktop/projects/volleyball_analytics/data/preprocessed/game-state'
    new_path = '/home/masoud/Desktop/projects/volleyball_analytics/data/processed/game-status'
    all_videos = list(Path(output_base_dir).rglob('*.mp4'))

    # services = [v for v in all_videos if v.parent.stem == 'service']
    noplay = [v for v in all_videos if v.parent.stem == 'play']
    inplay = [v for v in all_videos if v.parent.stem == 'no-play']
    service = [v for v in all_videos if v.parent.stem == 'service']

    test_size = 0.1

    for pack in [noplay, inplay, service]:
        shuffle(pack)
        test_length = int(len(pack) * test_size)
        for i, item in enumerate(pack):
            parent = item.parent.stem
            if i <= test_length:
                path = join(new_path, 'test', parent)
            else:
                path = join(new_path, 'train', parent)
            makedirs(path, exist_ok=True)
            move(item.as_posix(), path)  # This is a lot faster, but a little risky...
            # copy2(item.as_posix(), path)

    print("finished data split ....")
