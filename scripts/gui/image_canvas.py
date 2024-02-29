from tkinter import Canvas, Tk, PhotoImage
from PIL import Image, ImageTk
import cv2
import random

if __name__ == '__main__':
    """
    1. select an initial frame from video which can be random
    2. Use a button to change to another frame in the video if current one was unclear.
    3. keep the previous frame numbers, so we can use another button to get to previous ones.
    
    UI:
        1. insert 4 red points for the whole court annotation.
        2. insert 4 blue points for front zone annotation.
    
    After annotation:
        1. we get center line.
        2. we get attack lines.
        3. we get front zone of team A, and team B.
        4. we get each 1 - 6 zones for both teams.
    
    """

    file = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/8.mp4'
    cap = cv2.VideoCapture(file)
    assert cap.isOpened(), "file is not accessible."
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

    fno = random.randint(1, n_frames//10)
    cap.set(1, fno)
    _, frame = cap.read()
    image = cv2.cvtColor(frame, 4)
    image = Image.fromarray(image)

    root = Tk()
    canvas = Canvas(root, width=w+20, height=h+20, bg='black')
    canvas.pack(fill='both', expand=True)
    # image = cv2.imread(file)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=image, anchor="nw")
    logo = PhotoImage()

    root.mainloop()
