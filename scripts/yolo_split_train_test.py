from os import makedirs
from pathlib import Path
from os.path import join
from random import shuffle
from shutil import move

from natsort import natsorted

dataset_root = '/home/masoud/Desktop/projects/volleyball_analytics/data/preprocessed/6_classs_V2'
new_path = '/home/masoud/Desktop/projects/volleyball_analytics/data/processed/6_classs_V2'
all_images = natsorted(list(Path(dataset_root).rglob('*.png')), key=lambda x: x.stem)
all_labels = natsorted(list(Path(dataset_root).rglob('*.txt')), key=lambda x: x.stem)
pairs = list(zip(all_images, all_labels))


test_size = 0.1
test_length = int(len(pairs) * test_size)

shuffle(pairs)

for i, (img, lbl) in enumerate(pairs):
    if i <= test_length:
        img_path = join(new_path, 'images', 'test')
        lbl_path = join(new_path, 'labels', 'test')
    else:
        img_path = join(new_path, 'images', 'train')
        lbl_path = join(new_path, 'labels', 'train')
    makedirs(img_path, exist_ok=True)
    makedirs(lbl_path, exist_ok=True)
    move(img.as_posix(), img_path)
    move(lbl.as_posix(), lbl_path)

