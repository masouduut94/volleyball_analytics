import cv2
import numpy as np
import pandas as pd
from os.path import join
from pathlib import Path

"""
Data must be like this:
frame | x | y | toss | end_toss | exclude | exclude-end
"""
SKIP1 = 1
SKIP2 = 10
SKIP_WHEEL = 15
SKIP3 = 200
BBOX_ANNOTATION = True
global drag


def check_fno(fno, total_frame):
    """
    check if suggested frame number is not invalid based on video number of frames.
    Args:
        fno:
        total_frame:

    Returns:

    """
    if fno < 0:
        print('\nInvaild !!! Jump to first image...')
        return False
    if fno > total_frame:
        print(f"\n maximum frames = {total_frame}")
    else:
        print(f"Frame set to: {fno}")
        return True


def to_frame(cap, df, current_fno, total_frame, custom_msg=None):
    global current
    print('current frame: ', current_fno)
    if check_fno(current_fno, total_frame):
        current = current_fno
    cap.set(cv2.CAP_PROP_POS_FRAMES, current)
    ret, frame = cap.read()
    if not (current >= total_frame):
        message = init_message(df, current, msg_cols, custom_msg)
    else:
        df = save_data(df, save_path)
        print("frame index bigger than number of frames.")
    if not ret:
        return None

    cv2.putText(frame, f'Frame: {current}/{total_frame}', (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    if message != '':
        cv2.putText(frame, message, (100, 400), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    item = df.iloc[current]
    if BBOX_ANNOTATION:
        if item.x1 != -1:
            x1 = item.x1
            x2 = item.x2
            y1 = item.y1
            y2 = item.y2
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    else:
        if item.x != -1:
            color = (0, 0, 255)
            x = item.x
            y = item.y
            cv2.circle(frame, (x, y), 5, color, thickness=-1)
    return frame


def go_to_next(df: pd.DataFrame, column: str, value: bool, current: int, return_last=False):
    next_indexes = df.index[df.frame > current]
    msg = f"no more `{column}` after current value"
    if not len(next_indexes):
        print(msg)
        return None, msg

    temp = df[(df[column] == value) & (df.index.isin(next_indexes))]
    if len(temp):
        if return_last:
            return temp.iloc[-1].frame, ""
        return temp.iloc[0].frame, ""
    print(msg)
    return None, msg


def go_to_previous(df: pd.DataFrame, column: str, value: bool, current: int, return_first=False):
    next_indexes = df.index[df.frame < current]
    msg = f"no more `{column}` before current value"
    if not len(next_indexes):
        print(msg)
        return None, msg

    temp = df[(df[column] == value) & (df.index.isin(next_indexes))]
    if len(temp):
        if return_first:
            return temp.iloc[0].frame, ""
        return temp.iloc[-1].frame, ""
    print(msg)
    return None, msg


def click_and_crop(event, x, y, flags, param):  # noqa: C901
    # grab references to the global variables
    global data, cap, current
    global frame
    global drag
    global left_top, right_bottom
    print(flags)
    if BBOX_ANNOTATION:
        if event == cv2.EVENT_LBUTTONDOWN:
            left_top = (x, y)
            drag = 1
            df.at[current, 'x1'] = left_top[0]
            df.at[current, 'y1'] = left_top[1]
            print(f"left top: {left_top}")
            print("drag", drag)
        elif event == cv2.EVENT_MOUSEMOVE and flags == 1:
            # frame = to_frame(cap, df, current, n_frames)
            cap.set(1, current)
            status, frame = cap.read()
            cv2.rectangle(frame, left_top, (x, y), (0, 255, 0), 2)
            # print(f"right bottom: {right_bottom}")
            # df.at[current, 'x2'] = right_bottom[0]
            # df.at[current, 'y2'] = right_bottom[1]
            # frame = to_frame(cap, df, current, n_frames)
        elif event == cv2.EVENT_LBUTTONUP:
            drag = 0
            # right_bottom = (, y)
            df.at[current, 'x2'] = x
            df.at[current, 'y2'] = y
            frame = to_frame(cap, df, current, n_frames)
            # cv2.rectangle(image, left_top, right_bottom, (0, 255, 0), 2)
            # cv2.imshow("image", image)
    else:
        if event == cv2.EVENT_LBUTTONDOWN:
            df.at[current, 'x'] = x
            df.at[current, 'y'] = y

            frame = to_frame(cap, df, current, n_frames)

    if event == cv2.EVENT_MOUSEWHEEL:
        # print(flags)
        if flags == 7864320:
            current += SKIP1
        elif flags == -7864320:
            current -= SKIP1
        elif flags == 7864328:
            current += SKIP2
        elif flags == -7864312:
            current -= SKIP2
        elif flags == 7864336:
            current += SKIP3
        elif flags == -7864304:
            current -= SKIP3
        # current = (current + SKIP_WHEEL) if flags > 0 else (current - SKIP_WHEEL)
        frame = to_frame(cap, df, current, n_frames)


def init_message(df, index, columns, custom_msg=None):
    st = ''
    for col in columns:
        if df.at[index, col]:
            st += f'| {col}'

    st = custom_msg if custom_msg is not None else st

    return st


def turn_columns_into_int32(dataframe):
    if BBOX_ANNOTATION:
        for col in ['frame', 'x1', 'y1', 'x2', 'y2']:
            dataframe[col] = dataframe[col].astype('int32')
    else:
        for col in ['frame', 'x', 'y']:
            dataframe[col] = dataframe[col].astype('int32')


def init(dataframe: pd.DataFrame, columns_dtype: dict, with_fake_values: bool = False):
    frames = np.arange(0, n_frames)
    fake_positions = [-1] * n_frames
    fake_bool = [False] * n_frames
    if with_fake_values:
        if BBOX_ANNOTATION:
            data = {
                'frame': frames,
                'x1': fake_positions,
                'y1': fake_positions,
                'x2': fake_positions,
                'y2': fake_positions
            }
        else:
            data = {
                'frame': frames,
                'x': fake_positions,
                'y': fake_positions
            }
        dataframe = pd.DataFrame(data=data)

    turn_columns_into_int32(dataframe)

    for dtype, columns in columns_dtype.items():
        if dtype == 'int32':
            fake = np.array([-1] * n_frames)
            for col in columns:
                if with_fake_values:
                    dataframe[col] = fake
                dataframe[col] = dataframe[col].astype('int')
        elif dtype == 'bool':
            for col in columns:
                if with_fake_values:
                    dataframe[col] = fake_bool
                dataframe[col] = dataframe[col].astype(bool)
    return dataframe


def save_data(df, save_path):
    df = df.sort_values(by=['frame'])
    df.to_csv(save_path, index=False)
    print(f"data saved automatically in {save_path}")
    return df


if __name__ == '__main__':  # noqa: C901
    VIDEO_FILE = "data/videos/5.mp4"
    CSV_SAVE_PATH = 'data/videos'

    cols_dtype = {
        'bool': ['service', 'service_end', 'set', 'set_end', 'front_spike', 'middle_spike', 'back_spike', 'pipe_spike'],
        'int32': ['frame', 'x1', 'y1', 'x2', 'y2'] if BBOX_ANNOTATION else ['frame', 'x', 'y']}

    msg_cols = ['service', 'service_end', 'set', 'set_end', 'front_spike', 'middle_spike', 'back_spike', 'pipe_spike']

    cap = cv2.VideoCapture(VIDEO_FILE)
    assert cap.isOpened(), "file is not opened!"
    name = Path(VIDEO_FILE).stem
    save_path = join(CSV_SAVE_PATH, name + '.csv')

    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    try:
        df = pd.read_csv(save_path)
        df = init(df, cols_dtype)
        print(f"loading from csv file {save_path}")
    except KeyError:
        df = init(None, cols_dtype, with_fake_values=True)
        print(f"failed to load {save_path}. initializing ......")

    current = 0
    frame = to_frame(cap, df, current, n_frames)
    cv2.namedWindow("image", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("image", click_and_crop)

    while True:
        cv2.imshow("image", frame)
        key = cv2.waitKeyEx(1)
        if key == 27:
            df = save_data(df, save_path)
            custom_msg = "Data is saved ..."
            frame = to_frame(cap, df, current, n_frames, custom_msg=custom_msg)
            break
        if key == 3014656:
            if BBOX_ANNOTATION:
                df.at[current, "x1"] = -1
                df.at[current, "x2"] = -1
                df.at[current, "y1"] = -1
                df.at[current, "y2"] = -1
            else:
                df.at[current, 'x'] = -1
                df.at[current, 'y'] = -1

            custom_msg = "Data is reset ..."
            frame = to_frame(cap, df, current, n_frames, custom_msg=custom_msg)

        elif key == ord('1'):
            df.at[current, 'service'] = False if df.at[current, "service"] else True
            print(current, f" service: {df.at[current, 'service']}")
            df = save_data(df, save_path)
            frame = to_frame(cap, df, current, n_frames)
        elif key == ord('2'):
            df.at[current, 'service_end'] = False if df.at[current, "service_end"] else True
            df = save_data(df, save_path)
            frame = to_frame(cap, df, current, n_frames)
            print(current, f" service_end: {df.at[current, 'service_end']}")
        elif key == ord('3'):
            df.at[current, 'set'] = False if df.at[current, "set"] else True
            df = save_data(df, save_path)
            frame = to_frame(cap, df, current, n_frames)
            print(current, f" set: {df.at[current, 'set']}")
        elif key == ord('4'):
            df.at[current, 'set_end'] = False if df.at[current, "set_end"] else True
            df = save_data(df, save_path)
            frame = to_frame(cap, df, current, n_frames)
            print(current, f" set_end: {df.at[current, 'set_end']}")
        elif key == ord('s'):
            df = save_data(df, save_path)
            custom_msg = "Data is saved ..."
            frame = to_frame(cap, df, current, n_frames, custom_msg=custom_msg)
        elif key == ord('t'):
            next_frame, msg = go_to_next(df, column='set', value=True, current=current)
            if next_frame is not None:
                frame = to_frame(cap, df, next_frame, n_frames, custom_msg='jumping to next toss')
            else:
                frame = to_frame(cap, df, current, n_frames, custom_msg=msg)
        elif key == ord('g'):
            prev_frame, msg = go_to_previous(df, column='set', value=True, current=current)
            if prev_frame is not None:
                frame = to_frame(cap, df, prev_frame, n_frames, custom_msg='jumping to previous toss')
            else:
                frame = to_frame(cap, df, current, n_frames, custom_msg=msg)

        elif key == ord('q'):
            next_frame, msg = go_to_next(df, column='service', value=True, current=current)
            if next_frame is not None:
                frame = to_frame(cap, df, next_frame, n_frames, custom_msg='jumping to next toss_end')
            else:
                frame = to_frame(cap, df, current, n_frames, custom_msg=msg)
        elif key == ord('a'):
            prev_frame, msg = go_to_previous(df, column='service_end', value=True, current=current)
            if prev_frame is not None:
                frame = to_frame(cap, df, prev_frame, n_frames, custom_msg='jumping to previous toss_end')
            else:
                frame = to_frame(cap, df, current, n_frames, custom_msg=msg)
        elif key == ord("f"):
            try:
                check = int(input('Enter your frame:'))
            except KeyError:
                print("not a valid number.")
                check = current
            frame = to_frame(cap, df, check, n_frames)
