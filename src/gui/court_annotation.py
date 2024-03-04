import json
from tkinter import Canvas, Tk, Button
from PIL import Image, ImageTk
import cv2
import random

from mathutils.geometry import intersect_point_line
from numpy._typing import NDArray
from typing_extensions import List

from src.ml.yolo.court.segmentation import CourtSegmentor


class CourtAnnotator(object):
    def __init__(self, filename: str):
        self._x = None
        self._y = None
        cfg = {
            'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/court_segment/weights/best.pt',
            "labels": {0: 'court'}
        }
        self.segmentor = CourtSegmentor(cfg=cfg)
        self.filename = filename
        self.cap = cv2.VideoCapture(self.filename)
        assert self.cap.isOpened(), "file is not accessible."
        self.w, self.h, self.fps, _, self.n_frames = [int(self.cap.get(i)) for i in range(3, 8)]

        self.size = 20
        self.frame = self.get_frame()
        tl, dl, dr, tr = self.ml_guided_corners(self.frame)

        self.w_tl = tl[0]
        self.w_tr = tr[0]
        self.w_dl = dl[0]
        self.w_dr = dr[0]
        self.h_top = tl[1]
        self.h_down = dr[1]

        p1_top_left = (self.w_tl + 10, self.h_top + 100)
        p2_top_right = (self.w_tr + 50, self.h_top + 50)
        p3_down_left = (self.w_tl + 50, self.h_top + 350)
        p4_down_right = (self.w_tr + 50, self.h_top + 300)

        self.intersection1 = self.find_intersection(
            line_pt1=(self.w_tl, self.h_top),
            line_pt2=(self.w_dl, self.h_down),
            x=p1_top_left
        )
        self.intersection2 = self.find_intersection(
            line_pt1=(self.w_tr, self.h_top),
            line_pt2=(self.w_dr, self.h_down),
            x=p2_top_right
        )
        self.intersection3 = self.find_intersection(
            line_pt1=(self.w_tl, self.h_top),
            line_pt2=(self.w_dl, self.h_down),
            x=p3_down_left
        )
        self.intersection4 = self.find_intersection(
            line_pt1=(self.w_tr, self.h_top),
            line_pt2=(self.w_dr, self.h_down),
            x=p4_down_right
        )

        self.root = Tk()
        self.root.title("Court Annotation: ")
        self.canvas = Canvas(self.root, width=self.w + 20, height=self.h + 50, bg='black')
        image = ImageTk.PhotoImage(Image.fromarray(self.frame))
        self.canvas.create_image(0, 0, image=image, anchor="nw")
        self.court_corners()
        self.draw_court()
        self.attack_line_pts()
        self.draw_attack_zone()
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move)
        self.root.bind("s", self.save_pts)

        self.root.mainloop()

    def ml_guided_corners(self, frame: NDArray):
        """
        It assists us to find 4 corners of court based on the segmentation model output.
        Args:
            frame:

        Returns:

        """
        points = self.segmentor.predict(frame)
        tl, dl, dr, tr = self.segmentor.find_corners(frame, mask_points=points)
        return tl, dl, dr, tr

    @staticmethod
    def find_intersection(line_pt1: tuple, line_pt2: tuple, x: tuple):
        """
        This method finds the intersection point between point `x` and line
        that connects `line_pt1` and `line_pt2`.
        Args:
            line_pt1:
            line_pt2:
            x:

        Returns:
            the intersection point (x, y)
        """
        intersect = intersect_point_line(x, line_pt1, line_pt2)
        return intersect[0][0], intersect[0][1]

    def attack_line_pts(self):
        self.att_line_TL = self.canvas.create_oval(
            self.intersection1[0],
            self.intersection1[1],
            self.intersection1[0] + self.size,
            self.intersection1[1] + self.size,
            fill="yellow"
        )
        self.att_line_TR = self.canvas.create_oval(
            self.intersection2[0],
            self.intersection2[1],
            self.intersection2[0] + self.size,
            self.intersection2[1] + self.size,
            fill="green"
        )

        self.att_line_DL = self.canvas.create_oval(
            self.intersection3[0],
            self.intersection3[1],
            self.intersection3[0] + self.size,
            self.intersection3[1] + self.size,
            fill="purple"
        )

        self.att_line_DR = self.canvas.create_oval(
            self.intersection4[0],
            self.intersection4[1],
            self.intersection4[0] + self.size,
            self.intersection4[1] + self.size,
            fill="blue"
        )

    def court_corners(self):
        """
        Draws the court corner points.
        Returns:

        """
        self.court_TL = self.canvas.create_oval(
            self.w_tl, self.h_top, self.w_tl + self.size, self.h_top + self.size, fill="red"
        )
        self.court_DL = self.canvas.create_oval(
            self.w_dl, self.h_down, self.w_dl + self.size, self.h_down + self.size, fill="red"
        )
        self.court_TR = self.canvas.create_oval(
            self.w_tr, self.h_top, self.w_tr + self.size, self.h_top + self.size, fill="red"
        )
        self.court_DR = self.canvas.create_oval(
            self.w_dr, self.h_down, self.w_dr + self.size, self.h_down + self.size, fill="red"
        )

    def draw_court(self):
        self.court_top_line = self.draw_line_pt1_pt2(self.court_TL, self.court_TR, color='red')
        self.court_down_line = self.draw_line_pt1_pt2(self.court_DL, self.court_DR, color='red')
        self.court_left_line = self.draw_line_pt1_pt2(self.court_DL, self.court_TL, color='red')
        self.court_right_line = self.draw_line_pt1_pt2(self.court_DR, self.court_TR, color='red')

    def draw_attack_zone(self):
        self.attackline_top_line = self.draw_line_pt1_pt2(self.att_line_TL, self.att_line_TR, color='yellow')
        self.attackline_down_line = self.draw_line_pt1_pt2(self.att_line_DL, self.att_line_DR, color='yellow')
        self.attackline_left_line = self.draw_line_pt1_pt2(self.att_line_DL, self.att_line_TL, color='yellow')
        self.attackline_right_line = self.draw_line_pt1_pt2(self.att_line_DR, self.att_line_TR, color='yellow')

    def get_frame(self):
        """
        Selects a frame from video input.
        Returns:

        """
        n_frames = int(self.cap.get(7))
        fno = random.randint(1, n_frames)
        self.cap.set(1, fno)
        _, frame = self.cap.read()
        image = cv2.cvtColor(frame, 4)
        return image

    def draw_line_pt1_pt2(self, pt1: tuple, pt2: tuple, color: str):
        """
        It creates a line between `pt1` and `pt2`.

        Args:
            pt1:
            pt2:
            color:

        Returns:

        """
        coordination1 = self.canvas.coords(pt1)
        coordination2 = self.canvas.coords(pt2)
        x0 = (coordination1[0] + coordination1[2]) // 2
        y0 = (coordination1[1] + coordination1[3]) // 2
        x1 = (coordination2[0] + coordination2[2]) // 2
        y1 = (coordination2[1] + coordination2[3]) // 2
        return self.canvas.create_line(x0, y0, x1, y1, fill=color, width=3)

    def reset_lines(self):
        for item in [self.court_top_line, self.court_down_line,
                     self.court_left_line, self.court_right_line]:
            self.canvas.delete(item)
        self.draw_court()
        for item in [
            self.attackline_top_line,
            self.attackline_down_line,
            self.attackline_left_line,
            self.attackline_right_line
        ]:
            self.canvas.delete(item)
        self.draw_attack_zone()

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def move(self, event):
        """
        Function to call when trying to move the circles around the image
        Args:
            event:

        Returns:

        """
        delta_x = event.x - self._x
        delta_y = event.y - self._y
        self._x = event.x
        self._y = event.y
        self.canvas.move("current", delta_x, delta_y)
        self.reset_lines()

    @staticmethod
    def get_center(pt) -> List[int]:
        return [(pt[0] + pt[2]) // 2, (pt[1] + pt[3]) // 2]

    def save_pts(self, _event=None):
        print("saving coordination....")
        p0 = self.canvas.coords(self.court_TL)
        p1 = self.canvas.coords(self.court_DL)
        p2 = self.canvas.coords(self.court_TR)
        p3 = self.canvas.coords(self.court_DR)
        pt1 = self.get_center(p0)
        pt2 = self.get_center(p1)
        pt3 = self.get_center(p2)
        pt4 = self.get_center(p3)
        court_top_left, court_down_left, court_down_right, court_top_right = self.segmentor.find_corners(
            frame=self.frame,
            mask_points=[pt1, pt2, pt3, pt4]
        )

        p0 = self.canvas.coords(self.att_line_TL)
        p1 = self.canvas.coords(self.att_line_DL)
        p2 = self.canvas.coords(self.att_line_TR)
        p3 = self.canvas.coords(self.att_line_DR)
        pt1 = self.get_center(p0)
        pt2 = self.get_center(p1)
        pt3 = self.get_center(p2)
        pt4 = self.get_center(p3)
        att_top_left, att_down_left, att_down_right, att_top_right = self.segmentor.find_corners(
            frame=self.frame,
            mask_points=[pt1, pt2, pt3, pt4]
        )
        out_dict = {
            "main_zone": [court_top_left, court_down_left, court_down_right, court_top_right],
            "front_zone": [att_top_left, att_down_left, att_down_right, att_top_right]
        }
        json.dump(out_dict, open('output_json.json', 'w'))


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

    file = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/6.mp4'
    CourtAnnotator(filename=file)
