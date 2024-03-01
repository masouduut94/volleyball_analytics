from tkinter import Canvas, Tk, Button
from PIL import Image, ImageTk
import cv2
import random


class CourtAnnotator(object):
    def __init__(self, filename: str, ):
        self._x = None
        self._y = None
        cap = cv2.VideoCapture(file)
        assert cap.isOpened(), "file is not accessible."
        w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

        image = self.get_frame(cap)

        self.root = Tk()
        self.root.title("Court Annotation: ")
        self.canvas = Canvas(self.root, width=w + 20, height=h + 20, bg='black')
        self.canvas.pack()
        image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=image, anchor="nw")

        self.court_TL = self.canvas.create_oval(10, 10, 30, 30, fill="red")
        self.court_DL = self.canvas.create_oval(200, 200, 220, 220, fill="red")
        self.court_TR = self.canvas.create_oval(10, 400, 30, 420, fill="red")
        self.court_DR = self.canvas.create_oval(500, 400, 520, 420, fill="red")

        self.court_top_line = self.draw_line_pt1_pt2(self.court_TL, self.court_TR)
        self.court_down_line = self.draw_line_pt1_pt2(self.court_DL, self.court_DR)
        self.court_left_line = self.draw_line_pt1_pt2(self.court_DL, self.court_TL)
        self.court_right_line = self.draw_line_pt1_pt2(self.court_DR, self.court_TR)

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move)

        self.root.mainloop()

    @staticmethod
    def get_frame(cap: cv2.VideoCapture):
        n_frames = int(cap.get(7))
        fno = random.randint(1, n_frames)
        cap.set(1, fno)
        _, frame = cap.read()
        image = cv2.cvtColor(frame, 4)
        image = Image.fromarray(image)
        return image

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def draw_line_pt1_pt2(self, pt1, pt2):
        coordination1 = self.canvas.coords(pt1)
        coordination2 = self.canvas.coords(pt2)
        x0 = (coordination1[0] + coordination1[2]) // 2
        y0 = (coordination1[1] + coordination1[3]) // 2
        x1 = (coordination2[0] + coordination2[2]) // 2
        y1 = (coordination2[1] + coordination2[3]) // 2
        return self.canvas.create_line(x0, y0, x1, y1, fill='red', width=5)

    def reset_lines(self):
        self.canvas.delete(self.court_top_line)
        self.canvas.delete(self.court_down_line)
        self.canvas.delete(self.court_left_line)
        self.canvas.delete(self.court_right_line)

        self.court_top_line = self.draw_line_pt1_pt2(self.court_TL, self.court_TR)
        self.court_down_line = self.draw_line_pt1_pt2(self.court_DL, self.court_DR)
        self.court_left_line = self.draw_line_pt1_pt2(self.court_DL, self.court_TL)
        self.court_right_line = self.draw_line_pt1_pt2(self.court_DR, self.court_TR)

    def move(self, event):
        delta_x = event.x - self._x
        delta_y = event.y - self._y
        self._x = event.x
        self._y = event.y
        self.canvas.move("current", delta_x, delta_y)

        self.reset_lines()


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
    CourtAnnotator(filename=file)
