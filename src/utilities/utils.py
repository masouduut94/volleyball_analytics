import cv2
import math
from loguru import logger
import numpy as np
from time import time
from tqdm import tqdm
from pathlib import Path
from functools import wraps
from numpy.typing import NDArray


def video_write(input: str, output_path: str, yolo_model, config):
    action_detector = yolo_model(cfg=config)
    cap = cv2.VideoCapture(input)
    assert cap.isOpened()

    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_file = Path(output_path) / (Path(input).stem + '_output.mp4')
    writer = cv2.VideoWriter(output_file.as_posix(), fourcc, fps, (w, h))

    for fno in tqdm(list(range(n_frames))):
        cap.set(1, fno)
        status, frame = cap.read()
        bboxes = action_detector.predict(frame)
        frame = action_detector.draw(frame, bboxes)
        writer.write(frame)

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f'saved results in {output_file}')


def timeit(f):
    """A wrapper around function f that measures the execution time."""

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f'func:{f.__name__} took: {te - ts: .2f} sec')
        return result

    return wrap


def state_summarize(states):
    curr = states[0]
    temp = [curr]
    for item in states:
        if item == curr:
            continue
        else:
            curr = item
            temp.append(curr)
    return temp


class Meta:
    white = (255, 255, 255)
    black = (0, 0, 0)
    purple = (148, 0, 211)
    magenta = (255, 0, 255)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (255, 215, 0)
    orange = (255, 140, 0)
    brown = (205, 133, 63)
    pink = (240, 128, 128)
    red = (255, 0, 0)
    aqua = (0, 255, 255)
    grey = (128, 128, 128)

    bgr_purple = (211, 0, 148)
    bgr_blue = (255, 0, 0)
    bgr_red = (0, 0, 255)
    bgr_orange = (0, 140, 255)
    bgr_yellow = (0, 215, 255)
    bgr_pink = (128, 128, 240)
    bgr_brown = (63, 133, 205)
    bgr_aqua = (255, 255, 0)


class CourtCoordinates:
    def __init__(self, points: dict):
        main_zone = points['main_zone']
        front_zone = points['front_zone']
        self.main_zone = np.array(
            [main_zone],
            dtype=np.int32
        )
        self.front_zone = np.array(
            [front_zone],
            dtype=np.int32
        )

    def is_inside_main_zone(self, point: tuple):
        result = cv2.pointPolygonTest(self.main_zone, point, False)
        return result > 0

    def is_inside_front_zone(self, point: tuple):
        result = cv2.pointPolygonTest(self.front_zone, point, False)
        return result > 0


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
        return True if all((self.x1 < self.x2, self.y1 < self.y2)) else False

    @property
    def xyxy_dict(self):
        return {
            'x1': self.x1,
            'x2': self.x2,
            'y1': self.y1,
            'y2': self.y2,
            'conf': self.conf
        }

    @property
    def xywh(self):
        return {
            'x1': self.x1,
            'y1': self.y1,
            'w': self.width,
            'h': self.height
        }

    def __repr__(self):
        con = "Contour" if self.contour_type else "no Contour"
        if self.detected:
            return f"""name={self.name} | {con} | center={self.center} | box={self.box}"""
        else:
            return f"""name={self.name} | NOT detected!"""

    @classmethod
    def create(cls, x):
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
        center_x = self.x1 + int(self.width / 2)
        center_y = self.y1 + int(self.height / 2)
        return center_x, center_y

    def distance(self, coordination: np.ndarray):
        """
        Calculate distance between its center to given (x, y)
        References:
            https://www.geeksforgeeks.org/calculate-the-euclidean-distance-using-numpy/
        Args:

        Returns:
            the distance between bounding box and the given coordination
        """

        return np.round(np.linalg.norm(np.array(self.center) - coordination), 3)

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
        bbox = self.create(box)
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
    def down_center(self):
        x_center = (self.left_down[0] + self.right_down[0]) // 2
        y_center = (self.left_down[1] + self.right_down[1]) // 2
        return x_center, y_center

    @property
    def top_center(self):
        x_center = (self.left_top[0] + self.right_top[0]) // 2
        y_center = (self.left_top[1] + self.right_top[1]) // 2
        return x_center, y_center

    @property
    def diameter_size(self):
        return math.sqrt(self.width ** 2 + self.height ** 2)

    def plot(self, frame, color=None, title=None):
        img = frame.copy()
        if not self.contour_type:
            if not color:
                if self.name == "players":
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

    def draw_ellipse(self, img: NDArray, color: tuple = Meta.blue) -> NDArray:
        if not self.detected:
            return img
        img = cv2.ellipse(
            img,
            center=self.down_center,
            axes=(int((self.width - 10)), int(0.35 * (self.width - 10))),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )
        return img

    def draw_marker(self, img: np.ndarray, color: tuple = Meta.green) -> np.ndarray:
        if not self.detected:
            return img
        x = self.top_center[0]
        y = self.top_center[1]
        y_top = y - 10
        x_left = x - 10
        x_right = x + 10

        left = [x_left, y_top]
        right = [x_right, y_top]
        contour = np.array([left, [x, y], right], dtype=np.int32)  # Maybe float32
        img = cv2.fillPoly(img, [contour], color)
        # cv2.circle(img, left, 10, color, -2)
        # cv2.circle(img, right, 10, color, -2)
        # cv2.circle(img, self.top_center, 10, color, -2)

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
    def __init__(self, keypoints: NDArray, conf: float = 0, name: str = None):
        """Single players keypoints from single yolo. A frame will have a list of these objects.
        Args:
            keypoints:
            name:
        """
        self.name = name
        self.keypoints = keypoints.astype(int)
        self.conf = conf
        self.colors = np.random.randint(low=0, high=255, size=(7, 3))

        self.pose_pairs = {
            'green': [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)],
            'orange': [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10)],
            'purple': [(5, 11), (6, 12), (11, 12)],
            'blue': [(11, 13), (12, 14), (13, 15), (14, 16)]
        }
        self.box = self.get_bbox()

    def get_bbox(self):
        """Generates the BoundingBox for keypoints."""
        height_margin = 10
        width_margin = 10
        xs = self.keypoints[:, 0]
        xs = xs[xs != 0]
        ys = self.keypoints[:, 1]
        ys = ys[ys != 0]

        if not len(xs) or not len(ys):
            return BoundingBox([0, 0, 0, 0], name=self.name, conf=self.conf)

        min_x = np.min(xs) - width_margin if (np.min(xs) - width_margin) > 0 else np.min(xs)
        min_y = np.min(ys) - height_margin if (np.min(xs) - height_margin) > 0 else np.min(xs)
        max_x = np.max(xs) + width_margin
        max_y = np.max(ys) + height_margin

        return BoundingBox([min_x, min_y, max_x, max_y], name=self.name, conf=self.conf)

    @property
    def nose(self):
        return tuple(self.keypoints[0])

    @property
    def left_eye(self):
        return tuple(self.keypoints[1])

    @property
    def right_eye(self):
        return tuple(self.keypoints[2])

    @property
    def left_ear(self):
        return tuple(self.keypoints[3])

    @property
    def right_ear(self):
        return tuple(self.keypoints[4])

    @property
    def left_shoulder(self):
        return tuple(self.keypoints[5])

    @property
    def right_shoulder(self):
        return tuple(self.keypoints[6])

    @property
    def left_elbow(self):
        return tuple(self.keypoints[7])

    @property
    def right_elbow(self):
        return tuple(self.keypoints[8])

    @property
    def left_wrist(self):
        return tuple(self.keypoints[9])

    @property
    def right_wrist(self):
        return tuple(self.keypoints[10])

    @property
    def left_hip(self):
        return tuple(self.keypoints[11])

    @property
    def right_hip(self):
        return tuple(self.keypoints[12])

    @property
    def left_knee(self):
        return tuple(self.keypoints[13])

    @property
    def right_knee(self):
        return tuple(self.keypoints[14])

    @property
    def left_ankle(self):
        return tuple(self.keypoints[15])

    @property
    def right_ankle(self):
        return tuple(self.keypoints[16])

    @property
    def center(self):
        return self.get_bbox().center

    @staticmethod
    def is_kp_detected(kp):
        """
        In yolo-v8 when the kp is not detected, it returns 0, 0 for x, y ...
        Args:
            kp:

        Returns:

        """
        return kp[0] != 0 or kp[1] != 0

    @property
    def is_facing_to_camera(self):
        lw = self.left_wrist
        rw = self.right_wrist

        le = self.left_elbow
        re = self.right_elbow

        ls = self.left_shoulder
        rs = self.right_shoulder

        la = self.left_ankle
        ra = self.right_ankle

        lk = self.left_knee
        rk = self.right_knee

        if self.is_kp_detected(lw) and self.is_kp_detected(rw):
            return lw[0] > rw[0]
        elif self.is_kp_detected(le) and self.is_kp_detected(re):
            return le[0] > re[0]
        elif self.is_kp_detected(lk) and self.is_kp_detected(rk):
            return lk[0] > rk[0]
        elif self.is_kp_detected(ls) and self.is_kp_detected(rs):
            return ls[0] > rs[0]
        elif self.is_kp_detected(la) and self.is_kp_detected(ra):
            return la[0] > ra[0]

    def plot(self, img: NDArray) -> NDArray:
        for color, pairs in self.pose_pairs.items():
            for pair in pairs:
                pt1 = self.keypoints[pair[0]]
                pt2 = self.keypoints[pair[1]]
                if self.is_kp_detected(pt1) and self.is_kp_detected(pt2):
                    match color:
                        case 'green':
                            cv2.line(img, pt1, pt2, Meta.green, 2)
                        case 'orange':
                            cv2.line(img, pt1, pt2, Meta.orange, 2)
                        case 'purple':
                            cv2.line(img, pt1, pt2, Meta.purple, 2)
                        case 'blue':
                            cv2.line(img, pt1, pt2, Meta.blue, 2)
        return img

    def draw_ellipse(self, img: NDArray, color: tuple = Meta.blue) -> NDArray:
        return self.box.draw_ellipse(img=img, color=color)

    def draw_marker(self, img: np.ndarray, color: tuple = Meta.green) -> np.ndarray:
        return self.box.draw_marker(img=img, color=color)

    def json(self):
        # TODO: Needs integration with self.is_kp_detected...
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


class ProjectLogger:
    def __init__(self, filename: str = "logs.log"):
        self.logger = logger
        self.logger.add(sink=filename, format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}",
                        serialize=True)
        # if show:
        #     self.logger.add(sink=sys.stderr, format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}")

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def success(self, msg):
        self.logger.success(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
