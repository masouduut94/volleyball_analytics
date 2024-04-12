from shutil import move
from pathlib import Path
from os import makedirs
from os.path import join
from random import shuffle

dataset_root = '/home/masoud/Desktop/projects/volleyball_analytics/data/preprocessed/game-state-3-classes'
new_path = '/home/masoud/Desktop/projects/volleyball_analytics/data/processed/game-status'
all_videos = list(Path(dataset_root).rglob('*.mp4'))

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

