import cv2
import numpy as np
import math
from typing import List, Tuple
from numpy.typing import NDArray


class Meta:
    white = (255, 255, 255)
    black = (0, 0, 0)
    purple = (255, 0, 255)
    blue = (0, 255, 0)
    cyan = (0, 255, 255)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    orange = (255, 165, 0)
    red = (255, 0, 0)
    aqua = (21, 242, 253)


class BoundingBox:
    """
    Author:
        masoud Masoumi Moghadam: (masouduut94)
    Utility module which gets a numpy array of 4 items as input and
    can provide variety of tools related to bounding boxes.
    """

    def __init__(self, x, name=None, conf=0.0, contour=False):
        self.contour_type = contour
        if not contour:
            if isinstance(x, list):
                self.box = [int(i) for i in x]
            elif isinstance(x, dict):
                x1 = x['x1']
                x2 = x['x2']
                y1 = x['y1']
                y2 = x['y2']
                self.box = [int(i) for i in [x1, y1, x2, y2]]
            elif isinstance(x, np.ndarray):
                self.box = x.astype(int).tolist()
            self.contour = None
            self.x1 = self.box[0]
            self.y1 = self.box[1]
            self.x2 = self.box[2]
            self.y2 = self.box[3]

            self.max_x = max([self.x1, self.x2])
            self.min_x = min([self.x1, self.x2])
            self.max_y = max([self.y1, self.y2])
            self.min_y = min([self.y1, self.y2])

            self.width = abs(self.x1 - self.x2)
            self.height = abs(self.y1 - self.y2)
        else:
            self.contour = np.array([x[0], x[1], x[2], x[3]], dtype=np.float32)
            self.x1 = self.min_x = min([i[0] for i in x])
            self.x2 = self.max_x = max([i[0] for i in x])
            self.y1 = self.min_y = min([i[1] for i in x])
            self.y2 = self.max_y = max([i[1] for i in x])

        self.attributes = []
        self.count = 0
        self.deleted = 0
        self.conf = conf
        self.name = name
        self.random_color = tuple(np.random.randint(low=0, high=254, size=(3,)).tolist())

    def add_attribute(self, attribute):
        self.attributes.append(attribute)

    @property
    def detected(self):
        return True if self.x1 != -1 else False

    @property
    def xyxy_dict(self):
        return {
            'x1': self.x1,
            'x2': self.x2,
            'y1': self.y1,
            'y2': self.y2
        }

    @property
    def xyxy_np(self):
        return np.array([self.x1, self.y1, self.x2, self.y2])

    def __repr__(self):
        con = "Contour" if self.contour_type else "no Contour"
        if self.detected:
            return f"""name={self.name} | {con} | center={self.center} | box={self.box}"""
        else:
            return f"""name={self.name} | NOT detected!"""

    @classmethod
    def create_new(cls, x):
        """

        Args:
            x: list of 4 items indicating [x1, y1, x2, y2]

        Returns:
            instantiate a BoundingBox module in place.
        """
        return cls(x, name=None)

    @property
    def area(self):
        """
        Calculates the surface area. useful for IOU!
        """
        return (self.x2 - self.x1 + 1) * (self.y2 - self.y1 + 1)

    @property
    def center(self):
        """
        Attribute indicating the center of bbox
        Returns:

        """
        center_x = self.x1 + self.width // 2
        center_y = self.y1 + self.height // 2
        return np.array([center_x, center_y])

    def distance(self, coordination: np.ndarray):
        """
        Calculate distance between its center to given (x, y)
        References:
            https://www.geeksforgeeks.org/calculate-the-euclidean-distance-using-numpy/
        Args:

        Returns:

        """

        return np.round(np.linalg.norm(self.center - coordination), 3)

    def intersection(self, bbox):
        if isinstance(bbox, list):
            bbox = BoundingBox(bbox)
        x1 = max(self.x1, bbox.x1)
        y1 = max(self.y1, bbox.y1)
        x2 = min(self.x2, bbox.x2)
        y2 = min(self.y2, bbox.y2)
        intersection = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)
        return intersection

    def iou(self, box):
        """
        Calculates the intersection over union with bbox given
        References:
            https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
        Args:
            box: (iterable): it's a tuple/list/numpy array of 4 items x1, y1, x2, y2

        Returns:

        """
        bbox = self.create_new(box)
        intersection = self.intersection(bbox)

        iou = intersection / float(self.area + bbox.area - intersection)
        # return the intersection over union value
        return iou

    def frame_crop(self, frame, margin=None):
        """
        Crop a portion of the image
        Args:
            frame:
            margin:

        Returns:

        """
        h, w, _ = frame.shape
        if margin is not None:
            y1 = (self.y1 - margin) if (self.y1 - margin) > 0 else 0
            y2 = (self.y2 + margin) if (self.y2 + margin) < h else h
            x1 = (self.x1 - margin) if (self.x1 - margin) > 0 else 0
            x2 = (self.x2 + margin) if (self.x2 + margin) < w else w
            f = frame[y1: y2, x1: x2, :]
        else:
            f = frame[self.y1: self.y2, self.x1: self.x2, :]

        h, w, _ = f.shape
        pixels = abs(w - h)

        if w > h:
            f = cv2.copyMakeBorder(
                f, top=pixels // 2, bottom=pixels // 2,
                left=0, right=0,
                borderType=cv2.BORDER_CONSTANT
            )
        else:
            f = cv2.copyMakeBorder(
                f, top=0, bottom=0,
                left=pixels // 2, right=pixels // 2,
                borderType=cv2.BORDER_CONSTANT
            )
        return f

    def is_same_location(self, box, threshold):
        """
        Whether the bbox is in the same location of it used to be
        in previous frames (same location of the input box ).
        Args:
            box:
            threshold:

        Returns:

        """
        return True if self.iou(box) > threshold else False

    @property
    def left_top(self):
        return min(self.x1, self.x2), min(self.y1, self.y2)

    @property
    def left_down(self):
        return min(self.x1, self.x2), max(self.y1, self.y2)

    @property
    def right_top(self):
        return max(self.x1, self.x2), min(self.y1, self.y2)

    @property
    def right_down(self):
        return max(self.x1, self.x2), max(self.y1, self.y2)

    @property
    def diameter_size(self):
        return math.sqrt(self.width ** 2 + self.height ** 2)

    def plot(self, frame, color=None, title=None):
        img = frame.copy()
        if not self.contour_type:
            if not color:
                if self.name == "person":
                    color = (255, 0, 0)
                elif self.name == 'ball':
                    color = (0, 255, 0)
                else:
                    color = self.random_color
            img = cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), color=color, thickness=2)
            if title:
                img = cv2.putText(img, title, (self.x1, self.y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness=2)
            elif self.name:
                img = cv2.putText(img, self.name, (self.x1, self.y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness=2)
            if len(self.attributes):
                img = cv2.putText(img, " | ".join(self.attributes), (self.x1, self.y2 + 10), cv2.FONT_HERSHEY_SIMPLEX,
                                  0.6, color, thickness=2)
        else:
            color = (255, 0, 0) if not color else color
            img = cv2.drawContours(img, [self.contour.astype(int)], 0, color, 2)
        return img

    def center_plot(self, frame, color=None, title=None):
        img = frame.copy()
        if not color:
            if self.name == "person":
                color = (255, 0, 0)
            elif self.name == 'ball':
                color = (0, 255, 0)
            else:
                color = self.random_color
        img = cv2.circle(img, (self.center[0], self.center[1]), 4, color, -3)
        if title is not None:
            img = cv2.putText(img, str(title), (self.x1, self.y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness=2)
        return img

    def plot_with_margin(self, frame, margin=(0, 0)):
        x_cen, y_cen = self.center
        x1 = x_cen - margin[0]
        x2 = x_cen + margin[0]
        y1 = y_cen + margin[1]
        y2 = y_cen + margin[1]

        color = (0, 255, 0)
        img = cv2.rectangle(frame, (x1, y1), (x2, y2), color=color, thickness=2)
        title = 'Bbox + margin'
        img = cv2.putText(img, title, ((x1 + x2) // 2, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness=2)
        return img

    def is_inside(self, center):
        """
        Indicates if the point `center` falls inside the bounding box or not.
        Args:
            center:

        Returns:

        """
        x, y = center.tolist()
        if not self.contour_type:
            x_inside = False
            y_inside = False
            if self.x1 < x < self.x2:
                x_inside = True
            if self.y1 < y < self.y2:
                y_inside = True
            result = x_inside and y_inside
        else:
            result = cv2.pointPolygonTest(self.contour, (x, y), False)
            result = result > 0
        return result

    def to_txt(self):
        if self.detected:
            return f'{self.name} {self.conf:.2f} {self.x1} {self.y1} {self.x2} {self.y2}'
        else:
            return ''


class KeyPointBox:
    def __init__(self, keypoints: NDArray, bbox: BoundingBox, name: str = None):
        """
        Single person keypoints from single detection. A frame will have a list of these objects.
        Args:
            keypoints:
            name:
        """
        self.name = name
        self.keypoints = keypoints.astype(int)
        self.bbox = bbox
        self.points = []
        self.colors = np.random.randint(low=0, high=255, size=(7, 3))
        for i, (x, y, conf) in enumerate(self.keypoints):
            self.points.append((x, y))
        self.pose_pairs = [(0, 1), (0, 2), (1, 3), (2, 4), (5, 6), (5, 7), (7, 9), (5, 11), (6, 12),
                           (6, 8), (8, 10), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]

    @staticmethod
    def as_tuple(output_dict):
        return output_dict['x'], output_dict['y']

    @property
    def nose(self):
        return self.keypoints[0][0], self.keypoints[0][1]

    @property
    def left_eye(self):
        return self.keypoints[1][0], self.keypoints[1][1]

    @property
    def right_eye(self):
        return self.keypoints[2][0], self.keypoints[2][1]

    @property
    def left_ear(self):
        return self.keypoints[3][0], self.keypoints[3][1]

    @property
    def right_ear(self):
        return self.keypoints[4][0], self.keypoints[4][1]

    @property
    def left_shoulder(self):
        return self.keypoints[5][0], self.keypoints[5][1]

    @property
    def right_shoulder(self):
        return self.keypoints[6][0], self.keypoints[6][1]

    @property
    def between_shoulders(self):
        l_shoulder = self.left_shoulder
        l_x, l_y = l_shoulder[0], l_shoulder[1]
        r_shoulder = self.right_shoulder
        r_x, r_y = r_shoulder[0], r_shoulder[1]
        x_dif = abs(r_x - l_x)
        y_dif = abs(r_y - l_y)
        b_x = l_x + x_dif // 2 if l_x < r_x else r_x + x_dif // 2
        b_y = l_y + y_dif // 2 if l_y < r_y else r_y + y_dif // 2
        return b_x, b_y

    @property
    def left_elbow(self):
        return self.keypoints[7][0], self.keypoints[7][1]

    @property
    def right_elbow(self):
        return self.keypoints[8][0], self.keypoints[8][1]

    @property
    def left_wrist(self):
        return self.keypoints[9][0], self.keypoints[9][1]

    @property
    def right_wrist(self):
        return self.keypoints[10][0], self.keypoints[10][1]

    @property
    def left_hip(self):
        return self.keypoints[11][0], self.keypoints[11][1]

    @property
    def right_hip(self):
        return self.keypoints[12][0], self.keypoints[12][1]

    @property
    def between_hips(self):
        l_hip = self.left_hip
        l_x, l_y = l_hip[0], l_hip[0]
        r_hip = self.right_shoulder
        r_x, r_y = r_hip[1], r_hip[1]
        x_dif = abs(r_x - l_x)
        y_dif = abs(r_y - l_y)
        b_x = l_x + x_dif // 2 if l_x < r_x else r_x + x_dif // 2
        b_y = l_y + y_dif // 2 if l_y < r_y else r_y + y_dif // 2
        return b_x, b_y

    @property
    def left_knee(self):
        return self.keypoints[13][0], self.keypoints[13][1]

    @property
    def right_knee(self):
        return self.keypoints[14][0], self.keypoints[14][1]

    @property
    def left_ankle(self):
        return self.keypoints[15][0], self.keypoints[15][1]

    @property
    def right_ankle(self):
        return self.keypoints[16][0], self.keypoints[16][1]

    def plot(self, img: NDArray, align_numbers=True, align_line=False, hands_only=False) -> NDArray:
        if not hands_only:
            for i, (x, y, conf) in enumerate(self.keypoints):
                img = cv2.circle(img, (x, y), 8, Meta.white, -1)
                if align_numbers:
                    img = cv2.putText(img, str(i), (x - 4, y + 2), cv2.FONT_HERSHEY_SIMPLEX, .3, Meta.black)
        else:
            for i, (x, y, conf) in enumerate(self.keypoints[5:11]):
                img = cv2.circle(img, (x, y), 8, Meta.white, -1)
                if align_numbers:
                    img = cv2.putText(img, str(i), (x - 4, y + 2), cv2.FONT_HERSHEY_SIMPLEX, .3, Meta.black)
                    # img, text, org, fontFace, fontScale, color[, thickness[, lineType
        if hands_only:
            align_line = True
        if align_line:
            points_colors = {
                (0, 1): Meta.red,
                (0, 2): Meta.red,
                (1, 3): Meta.orange,
                (2, 4): Meta.orange,
                (5, 7): Meta.yellow,
                (6, 8): Meta.yellow,
                (8, 10): Meta.aqua,
                (7, 9): Meta.aqua,
                (12, 14): Meta.cyan,
                (11, 13): Meta.cyan,
                (14, 16): Meta.blue,
                (13, 15): Meta.blue,
                (11, 12): Meta.purple,
                (5, 6): Meta.purple,
                (5, 11): Meta.purple,
                (6, 12): Meta.purple,
                (0, 'b_sh'): Meta.purple
            }
            if not hands_only:
                for pair in self.pose_pairs:
                    part_a = pair[0]
                    part_b = pair[1]
                    cv2.line(img, self.points[part_a], self.points[part_b], points_colors[pair], 2)
                b_shoulder = self.between_shoulders
                b_sh_x, b_sh_y = b_shoulder
                cv2.line(img, self.points[0], (b_sh_x, b_sh_y), points_colors[(0, 'b_sh')], 2)
            else:
                for pair in ((5, 6), (5, 7), (7, 9), (6, 8), (8, 10)):
                    part_a = pair[0]
                    part_b = pair[1]
                    cv2.line(img, self.points[part_a], self.points[part_b], points_colors[pair], 2)
        return img

    def json(self):
        js = {
            'nose': self.nose,
            'left_eye': self.left_eye,
            'right_eye': self.right_eye,
            'left_ear': self.left_ear,
            'right_ear': self.right_ear,
            'left_shoulder': self.left_shoulder,
            'right_shoulder': self.right_shoulder,
            'left_elbow': self.left_elbow,
            'right_elbow': self.right_elbow,
            'left_wrist': self.left_wrist,
            'right_wrist': self.right_wrist,
            'left_hip': self.left_hip,
            'right_hip': self.right_hip,
            'left_knee': self.left_knee,
            'right_knee': self.right_knee,
            'left_ankle': self.left_ankle,
            'right_ankle': self.right_ankle
        }
        return js
