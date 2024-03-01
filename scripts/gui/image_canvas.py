from tkinter import Canvas, Tk, Button
from PIL import Image, ImageTk
import cv2
import random


class CourtAnnotator(object):
    def __init__(self, filename: str, ):
        self._x = None
        self._y = None
        cap = cv2.VideoCapture(filename)
        assert cap.isOpened(), "file is not accessible."
        w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]

        w_tl = w // 4
        w_tr = w * 3 / 4
        w_dl = w // 30
        w_dr = w * 29 / 30

        h_tl = h / 2.5
        h_dr = h * 29 / 30

        image = self.get_frame(cap)

        self.root = Tk()
        self.root.title("Court Annotation: ")
        self.canvas = Canvas(self.root, width=w + 20, height=h + 50, bg='black')

        image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=image, anchor="nw")

        self.court_TL = self.canvas.create_oval(w_tl, h_tl, w_tl+30, h_tl+30, fill="red")
        self.court_DL = self.canvas.create_oval(w_dl, h_dr, w_dl+30, h_dr+30, fill="red")
        self.court_TR = self.canvas.create_oval(w_tr, h_tl, w_tr+30, h_tl+30, fill="red")
        self.court_DR = self.canvas.create_oval(w_dr, h_dr, w_dr+30, h_dr+30, fill="red")

        self.court_top_line = self.draw_line_pt1_pt2(self.court_TL, self.court_TR)
        self.court_down_line = self.draw_line_pt1_pt2(self.court_DL, self.court_DR)
        self.court_left_line = self.draw_line_pt1_pt2(self.court_DL, self.court_TL)
        self.court_right_line = self.draw_line_pt1_pt2(self.court_DR, self.court_TR)

        self.frame_changer = Button(self.root, width=20, height=2)
        self.frame_changer.configure(text="click to change frame", bg='grey')
        self.frame_changer.place(x=w // 2, y=h - 10)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move)
        # self.canvas.bind("<ButtonPress-1>", self.start_move)

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
