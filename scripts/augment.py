import cv2
from tqdm import tqdm
from pathlib import Path
from os.path import join
from natsort import natsorted

data_path = '/home/masoud/Desktop/projects/volleyball_analytics/data/processed/game-status-2-classes/train'

all_videos = natsorted(list(Path(data_path).rglob('*.mp4')), key=lambda x: x.parent.stem)
progress_bar = tqdm(all_videos)

for video_path in all_videos:
    progress_bar.set_description(f'progressing {video_path.parent.stem} path')
    progress_bar.update(1)
    name = video_path.stem + '__LR_flipped.mp4'
    save_path = video_path.parent.as_posix()

    cap = cv2.VideoCapture(video_path.as_posix())
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    filename = join(save_path, name)
    writer = cv2.VideoWriter(
        filename,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (w, h)
    )

    for fno in range(n_frames):
        status, frame = cap.read()
        # transformed = np.fliplr(frame)
        transformed = frame[:, ::-1]
        writer.write(transformed)
    writer.release()
    cap.release()
progress_bar.close()
