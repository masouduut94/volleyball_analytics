from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPen, QBrush, QColor, QPixmap, QFont
from PySide6.QtCore import Qt

from .geometry import POINTS, LINES


class PointItem(QGraphicsEllipseItem):
    """
    Draggable annotation point.
    """

    def __init__(self, name, label, x, y):
        super().__init__(-6, -6, 12, 12)

        self.name = name

        self.setPos(x, y)

        self.setBrush(QBrush(Qt.red))
        self.setPen(QPen(Qt.black, 1))

        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)

        self.text = QGraphicsTextItem(label)

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)

        self.text.setFont(font)
        self.text.setDefaultTextColor(Qt.yellow)

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            self.text.setPos(value.x() + 6, value.y() + 6)

            if self.scene():
                self.scene().update_lines()

        return super().itemChange(change, value)


class CourtScene(QGraphicsScene):
    """
    Court annotation scene.


    IMPORTANT:
    The scene persists across frame changes.
    Only the background image changes.
    Annotation points remain untouched.
    """

    def __init__(self, pixmap: QPixmap):
        super().__init__()

        self.background_item = QGraphicsPixmapItem(pixmap)
        self.background_item.setZValue(-10)  # Put background behind everything
        self.addItem(self.background_item)

        self.points = {}
        self.line_items = []

        self.create_default_points()

    # ---------------------------------------------------
    # Background handling
    # ---------------------------------------------------

    def set_background(self, pixmap: QPixmap):
        self.background_item.setPixmap(pixmap)

        self.setSceneRect(self.background_item.boundingRect())

    # ---------------------------------------------------
    # Default point creation
    # ---------------------------------------------------

    def create_default_points(self):
        rect = self.background_item.boundingRect()

        w = rect.width()
        h = rect.height()

        defaults = {
            "far_end_line_left": (w * 0.25, h * 0.15),
            "far_end_line_right": (w * 0.75, h * 0.15),
            "far_attack_line_left": (w * 0.28, h * 0.30),
            "far_attack_line_right": (w * 0.72, h * 0.30),
            "middle_line_left": (w * 0.30, h * 0.50),
            "middle_line_right": (w * 0.70, h * 0.50),
            "near_attack_line_left": (w * 0.28, h * 0.70),
            "near_attack_line_right": (w * 0.72, h * 0.70),
            "near_end_line_left": (w * 0.22, h * 0.90),
            "near_end_line_right": (w * 0.78, h * 0.90),
            "net_top_left": (w * 0.32, h * 0.47),
            "net_top_right": (w * 0.68, h * 0.47),
            "net_bottom_left": (w * 0.32, h * 0.53),
            "net_bottom_right": (w * 0.68, h * 0.53),
        }

        for name, abbr in POINTS.items():
            x, y = defaults[name]

            point = PointItem(name, abbr, x, y)
            point.setZValue(2)
            point.text.setZValue(3)

            self.addItem(point)
            self.addItem(point.text)

            point.text.setPos(x + 6, y + 6)

            self.points[name] = point

        self.update_lines()

    # ---------------------------------------------------
    # Load annotation from database
    # ---------------------------------------------------

    def load_points(self, data):
        for name, pt in data.items():
            if name in self.points:
                self.points[name].setPos(pt[0], pt[1])

        self.update_lines()

    # ---------------------------------------------------
    # Export annotation
    # ---------------------------------------------------

    def get_points(self):
        return {
            name: [item.pos().x(), item.pos().y()]
            for name, item in self.points.items()
        }

    # ---------------------------------------------------
    # Auto annotation support
    # ---------------------------------------------------

    def set_corner_points(self, corners):
        """
        corners:
        {
            'far_end_line_left': [x,y],
            'far_end_line_right': [x,y],
            'near_end_line_left': [x,y],
            'near_end_line_right': [x,y],
        }
        """

        for key, value in corners.items():
            if key in self.points:
                self.points[key].setPos(value[0], value[1])

        self.calculate_remaining_points()

    def calculate_remaining_points(self):
        """
        Estimate remaining points from the 4 detected corners.
        """

        fel = self.points["far_end_line_left"].pos()
        fer = self.points["far_end_line_right"].pos()
        nel = self.points["near_end_line_left"].pos()
        ner = self.points["near_end_line_right"].pos()

        def interpolate(p1, p2, t):
            return (
                p1.x() * (1 - t) + p2.x() * t,
                p1.y() * (1 - t) + p2.y() * t,
            )

        far_attack_left = interpolate(fel, nel, 0.25)
        far_attack_right = interpolate(fer, ner, 0.25)

        middle_left = interpolate(fel, nel, 0.50)
        middle_right = interpolate(fer, ner, 0.50)

        near_attack_left = interpolate(fel, nel, 0.75)
        near_attack_right = interpolate(fer, ner, 0.75)

        self.points["far_attack_line_left"].setPos(*far_attack_left)
        self.points["far_attack_line_right"].setPos(*far_attack_right)

        self.points["middle_line_left"].setPos(*middle_left)
        self.points["middle_line_right"].setPos(*middle_right)

        self.points["near_attack_line_left"].setPos(*near_attack_left)
        self.points["near_attack_line_right"].setPos(*near_attack_right)

        net_left = interpolate(fel, nel, -0.30)
        net_right = interpolate(fer, ner, -0.30)

        offset = 40

        self.points["net_top_left"].setPos(net_left[0], net_left[1] - offset)
        self.points["net_bottom_left"].setPos(net_left[0], net_left[1] + offset)

        self.points["net_top_right"].setPos(net_right[0], net_right[1] - offset)
        self.points["net_bottom_right"].setPos(net_right[0], net_right[1] + offset)

        self.update_lines()

    # ---------------------------------------------------
    # Colored line drawing
    # ---------------------------------------------------

    def update_lines(self):
        for item in self.line_items:
            self.removeItem(item)

        self.line_items.clear()

        RED = QPen(QColor(255, 0, 0), 4)
        YELLOW = QPen(QColor(255, 255, 0), 4)
        BLUE = QPen(QColor(0, 128, 255), 4)
        GREEN = QPen(QColor(0, 255, 0), 4)

        RED.setCapStyle(Qt.RoundCap)
        YELLOW.setCapStyle(Qt.RoundCap)
        BLUE.setCapStyle(Qt.RoundCap)
        GREEN.setCapStyle(Qt.RoundCap)

        for a, b in LINES:

            if a.startswith("net"):
                pen = BLUE

            elif "end_line" in a:
                pen = RED

            elif "attack" in a:
                pen = YELLOW

            elif "middle" in a:
                pen = GREEN

            else:
                pen = YELLOW

            pa = self.points[a].pos()
            pb = self.points[b].pos()

            line = self.addLine(
                pa.x(),
                pa.y(),
                pb.x(),
                pb.y(),
                pen,
            )

            line.setZValue(0)

            self.line_items.append(line)
