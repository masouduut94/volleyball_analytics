import json
from pathlib import Path
from tkinter import Canvas, Tk
from PIL import Image, ImageTk
import cv2
import random

from mathutils import Vector
from mathutils.geometry import intersect_point_line
from numpy._typing import NDArray
from typing_extensions import Tuple

from src.ml.yolo.court.segmentation import CourtSegmentor


class CourtAnnotator(object):
    def __init__(self, filename: str, save_path: str):
        self._x = None
        self._y = None
        cfg = {
            'weight': '/home/masoud/Desktop/projects/volleyball_analytics/weights/court_segment/weights/best.pt',
            "labels": {0: 'court'}
        }
        self.segmentor = CourtSegmentor(cfg=cfg)
        self.save_path = save_path
        self.save_file = Path(self.save_path) / 'reference_pts.json'
        self.filename = filename
        annots = None

        self.cap = cv2.VideoCapture(self.filename)
        assert self.cap.isOpened(), "file is not accessible."
        self.w, self.h, self.fps, _, self.n_frames = [int(self.cap.get(i)) for i in range(3, 8)]

        self.size = 20
        self.frame = self.get_frame()

        if self.save_file.is_file():
            js_file = json.load(open(self.save_file.as_posix()))
            try:
                annots = js_file[Path(self.filename).name]
            except KeyError:
                annots = None

        print(f"ANNOTS: {annots}")
        if annots is not None:
            print("USING PRE-ANNOTATED JSON")
            (self.w_tl, self.h_top), (self.w_dl, self.h_down), (self.w_dr, _), (self.w_tr, _) = annots['court']
            self.net_top_left, self.net_down_left, self.net_down_right, self.net_top_right = annots['net']
        else:
            print("Annotation not found. USING AI TO DETECT COURT ....")

            tl, dl, dr, tr = self.ml_guided_corners(self.frame)

            self.w_tl = tl[0]
            self.w_tr = tr[0]
            self.w_dl = dl[0]
            self.w_dr = dr[0]
            self.h_top = tl[1]
            self.h_down = dr[1]

            self.net_top_left = (self.w_tl, self.h_top - 400)
            self.net_down_left = (self.w_tl, self.h_top - 200)
            self.net_top_right = (self.w_tr, self.h_top - 400)
            self.net_down_right = (self.w_tr, self.h_top - 200)

        if annots is None:
            p1_top_left = (self.w_tl + 10, self.h_top + 100)
            p2_top_right = (self.w_tr + 50, self.h_top + 50)
            p3_down_left = (self.w_tl + 50, self.h_top + 350)
            p4_down_right = (self.w_tr + 50, self.h_top + 300)

            self.att_top_left = self.find_intersection(
                line_pt1=(self.w_tl, self.h_top),
                line_pt2=(self.w_dl, self.h_down),
                x=p1_top_left
            )
            self.att_top_right = self.find_intersection(
                line_pt1=(self.w_tr, self.h_top),
                line_pt2=(self.w_dr, self.h_down),
                x=p2_top_right
            )
            self.att_down_left = self.find_intersection(
                line_pt1=(self.w_tl, self.h_top),
                line_pt2=(self.w_dl, self.h_down),
                x=p3_down_left
            )
            self.att_down_right = self.find_intersection(
                line_pt1=(self.w_tr, self.h_top),
                line_pt2=(self.w_dr, self.h_down),
                x=p4_down_right
            )
        else:
            self.att_top_left, self.att_down_left, self.att_down_right, self.att_top_right = annots['attack']
        self.root = Tk()
        self.root.title("Court Annotation: ")
        self.canvas = Canvas(self.root, width=self.w + 20, height=self.h + 50, bg='black')
        image = ImageTk.PhotoImage(Image.fromarray(self.frame))
        self.canvas.create_image(0, 0, image=image, anchor="nw")

        self.pt1 = (self.w_tl, self.h_top)
        self.pt2 = (self.w_dl, self.h_down)
        self.pt3 = (self.w_dr, self.h_down)
        self.pt4 = (self.w_tr, self.h_top)

        self.court_oval_tl, self.court_oval_dl, self.court_oval_dr, self.court_oval_tr = \
            self.create_zone_corners(
                self.pt1,
                self.pt2,
                self.pt3,
                self.pt4,
                fill='green'
            )
        self.court_top_line, self.court_left_line, self.court_down_line, self.court_right_line = \
            self.create_zone_lines(
                self.court_oval_tl,
                self.court_oval_dl,
                self.court_oval_dr,
                self.court_oval_tr,
                color='green'
            )

        self.att_oval_tl, self.att_oval_dl, self.att_oval_dr, self.att_oval_tr = \
            self.create_zone_corners(
                pt1=self.att_top_left,
                pt2=self.att_down_left,
                pt3=self.att_down_right,
                pt4=self.att_top_right,
                fill='yellow'
            )
        self.att_top_line, self.att_left_line, self.att_down_line, self.att_right_line = \
            self.create_zone_lines(
                oval_tl=self.att_oval_tl,
                oval_dl=self.att_oval_dl,
                oval_dr=self.att_oval_dr,
                oval_tr=self.att_oval_tr,
                color='yellow'
            )

        self.net_oval_tl, self.net_oval_dl, self.net_oval_dr, self.net_oval_tr = \
            self.create_zone_corners(
                self.net_top_left,
                self.net_down_left,
                self.net_down_right,
                self.net_top_right,
                fill='red'
            )
        self.net_top_line, self.net_left_line, self.net_down_line, self.net_right_line = \
            self.create_zone_lines(
                self.net_oval_tl,
                self.net_oval_dl,
                self.net_oval_dr,
                self.net_oval_tr,
                color='red'
            )

        self.draw_center_line()
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
    def find_intersection(line_pt1: tuple, line_pt2: tuple, x: tuple) -> Tuple[int, int]:
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
        line_pt1 = Vector(line_pt1)
        line_pt2 = Vector(line_pt2)
        x = Vector(x)

        intersect = intersect_point_line(x, line_pt1, line_pt2)
        return intersect[0][0], intersect[0][1]

    def create_zone_corners(self, pt1: tuple, pt2: tuple, pt3: tuple, pt4: tuple, fill: str):
        """
        Creates 4 ovals as 4 corners of a rectangle.
        Args:
            pt1: top-left corner point.
            pt2: down-left corner point.
            pt3: down-right corner point.
            pt4: top-right corner point.
            fill: the color assigned to tkinter object.

        Returns:

        """
        court_top_left = self.canvas.create_oval(pt1[0], pt1[1], pt1[0] + self.size, pt1[1] + self.size, fill="green")
        court_down_left = self.canvas.create_oval(pt2[0], pt2[1], pt2[0] + self.size, pt2[1] + self.size, fill="purple")
        court_down_right = self.canvas.create_oval(pt3[0], pt3[1], pt3[0] + self.size, pt3[1] + self.size, fill="cyan")
        court_top_right = self.canvas.create_oval(pt4[0], pt4[1], pt4[0] + self.size, pt4[1] + self.size, fill="red")
        return court_top_left, court_down_left, court_down_right, court_top_right

    def create_zone_lines(self, oval_tl, oval_dl, oval_dr, oval_tr, color):
        top_line = self.draw_line_pt1_pt2(oval_tl, oval_tr, color=color)
        down_line = self.draw_line_pt1_pt2(oval_dl, oval_dr, color=color)
        left_line = self.draw_line_pt1_pt2(oval_dl, oval_tl, color=color)
        right_line = self.draw_line_pt1_pt2(oval_dr, oval_tr, color=color)
        return top_line, left_line, down_line, right_line

    def draw_center_line(self):
        """Uses the coordination of attack line ovals, and draws the center line."""

        TL = self.canvas.coords(self.att_oval_tl)
        DL = self.canvas.coords(self.att_oval_dl)
        TR = self.canvas.coords(self.att_oval_tr)
        DR = self.canvas.coords(self.att_oval_dr)

        TL_pt = self.get_center(TL)
        DL_pt = self.get_center(DL)
        TR_pt = self.get_center(TR)
        DR_pt = self.get_center(DR)

        self.left_center = int((TL_pt[0] + DL_pt[0]) / 2), int((TL_pt[1] + DL_pt[1]) / 2)
        self.right_center = int((TR_pt[0] + DR_pt[0]) / 2), int((TR_pt[1] + DR_pt[1]) / 2)

        self.center_line = self.draw_line_pt1_pt2(self.left_center, self.right_center, color='yellow')

    def get_frame(self):
        """
        Selects a random frame from video input.
        Returns:

        """
        n_frames = int(self.cap.get(7))
        fno = random.randint(1, n_frames)
        self.cap.set(1, fno)
        _, frame = self.cap.read()
        image = cv2.cvtColor(frame, 4)
        return image

    def draw_line_pt1_pt2(self, pt1: int | Tuple[int, int], pt2: int | Tuple[int, int], color: str):
        """
        It creates a line between `pt1` and `pt2`.

        Args:
            pt1:
            pt2:
            color:

        Returns:

        """
        if isinstance(pt1, int):
            coordination1 = self.canvas.coords(pt1)
            x0 = (coordination1[0] + coordination1[2]) // 2
            y0 = (coordination1[1] + coordination1[3]) // 2
        else:
            x0 = pt1[0]
            y0 = pt1[1]

        if isinstance(pt2, int):
            coordination2 = self.canvas.coords(pt2)
            x1 = (coordination2[0] + coordination2[2]) // 2
            y1 = (coordination2[1] + coordination2[3]) // 2
        else:
            x1 = pt2[0]
            y1 = pt2[1]
        return self.canvas.create_line(x0, y0, x1, y1, fill=color, width=3)

    def reset_lines(self):
        """To apply the actions assigned to objects, it removes and rebuilds the objects."""
        for item in [self.court_top_line, self.court_down_line,
                     self.court_left_line, self.court_right_line]:
            self.canvas.delete(item)
        self.court_top_line, self.court_down_line, self.court_left_line, self.court_right_line = \
            self.create_zone_lines(
                self.court_oval_tl,
                self.court_oval_dl,
                self.court_oval_dr,
                self.court_oval_tr,
                color="green"
            )
        for item in [
            self.att_top_line,
            self.att_down_line,
            self.att_left_line,
            self.att_right_line,
            self.center_line
        ]:
            self.canvas.delete(item)

        self.att_top_line, self.att_down_line, self.att_left_line, self.att_right_line = \
            self.create_zone_lines(
                self.att_oval_tl,
                self.att_oval_dl,
                self.att_oval_dr,
                self.att_oval_tr,
                color="yellow"
            )
        self.draw_center_line()

        for item in [self.net_top_line, self.net_down_line,
                     self.net_left_line, self.net_right_line]:
            self.canvas.delete(item)
        self.net_top_line, self.net_down_line, self.net_left_line, self.net_right_line = \
            self.create_zone_lines(
                self.net_oval_tl,
                self.net_oval_dl,
                self.net_oval_dr,
                self.net_oval_tr,
                color="red"
            )

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
    def get_center(pt) -> Tuple[int, int]:
        return int((pt[0] + pt[2]) / 2), int((pt[1] + pt[3]) / 2)

    def get_coords(self, oval_1, oval_2, oval_3, oval_4):
        find_coordinations = lambda a, b, c, d: [self.canvas.coords(i) for i in [a, b, c, d]]

        p1, p2, p3, p4 = find_coordinations(oval_1, oval_2, oval_3, oval_4)
        pt1, pt2, pt3, pt4 = [self.get_center(pt) for pt in [p1, p2, p3, p4]]
        court_coords = self.segmentor.find_corners(frame=self.frame, mask_points=[pt1, pt2, pt3, pt4])
        return court_coords

    def save_pts(self, _event=None):
        """If we press 's' on keyboard, this method saves all the coordination in a json file."""
        print("saving coordination....")

        court_coords = self.get_coords(self.court_oval_tl, self.court_oval_dl, self.court_oval_tr, self.court_oval_dr)
        att_line_coords = self.get_coords(self.att_oval_tl, self.att_oval_dl, self.att_oval_tr, self.att_oval_dr)
        net_coords = self.get_coords(self.net_oval_tl, self.net_oval_dl, self.net_oval_tr, self.net_oval_dr)

        if not self.save_file.is_file():
            out_dict = {
                Path(self.filename).name: {
                    "court": court_coords,
                    "attack": att_line_coords,
                    "center": (self.left_center, self.right_center),
                    "net": net_coords
                }}
            json.dump(out_dict, open(self.save_file.as_posix(), 'w'), sort_keys=True, indent=4)
        else:
            js = json.load(open(self.save_file.as_posix()))
            js[Path(self.filename).name] = {
                "court": court_coords,
                "attack": att_line_coords,
                "center": (self.left_center, self.right_center),
                "net": net_coords
            }
            json.dump(js, open(self.save_file.as_posix(), 'w'), sort_keys=True, indent=4)


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

    file = '/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/11.mp4'
    save_path = '/home/masoud/Desktop/projects/volleyball_analytics/conf'
    CourtAnnotator(filename=file, save_path=save_path)
