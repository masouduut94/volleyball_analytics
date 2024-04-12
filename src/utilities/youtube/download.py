
from tqdm import tqdm
from pytube import YouTube


# links = [
#     # 'https://www.youtube.com/watch?v=AAN1vhtvMpk',
#     # 'https://www.youtube.com/watch?v=chwVawzUgeE',
#     # 'https://www.youtube.com/watch?v=HrNeaWdl1JE',
#     # 'https://www.youtube.com/watch?v=ppmHlbJfSjg',
#     'https://www.youtube.com/watch?v=4lAVCyObCcE',
#     'https://www.youtube.com/watch?v=KmBAqyA6jfk'
# ]


v_links = [
    'https://www.youtube.com/watch?v=GmsP3ErGiLk',
    'https://www.youtube.com/watch?v=HSMMPl3iHiE',
    'https://www.youtube.com/watch?v=P9bmiyNQoMs',
    'https://www.youtube.com/watch?v=ESDQaH2wKL0',
    'https://www.youtube.com/watch?v=IYwAGz7BhXY',
    'https://www.youtube.com/watch?v=DWq7lRpvaLw',
    'https://www.youtube.com/watch?v=hHXyJ-Qm-XE'
]


for link in tqdm(v_links):
    yt = YouTube(link)
    print(link)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    # stream = yt.streams.first()
    stream.download('./')
