import cv2
from pathlib import Path
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QGraphicsView,
    QToolBar,
    QToolButton
)
from PySide6.QtGui import (
    QPixmap,
    QImage,
    QAction,
)

from .scene import CourtScene
from .geometry import build_polygons
from .yolo_config_dialog import YoloConfigDialog


class GraphicsView(QGraphicsView):
    """
    Simple zoomable graphics view.
    """

    def wheelEvent(self, event):
        factor = 1.15

        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1 / factor, 1 / factor)


class CalibrationWindow(QMainWindow):

    def __init__(self, video_path, db):
        super().__init__()

        self.display_width = 960
        self.display_height = 540

        self.scale_x = 1.0
        self.scale_y = 1.0

        self.db = db
        self.video_path = Path(video_path) if video_path else None

        self.frame_index = 0
        self.scene = None
        self.result = None
        self.current_frame = None

        self.setWindowTitle("Volleyball Court Calibration")
        self.resize(1000, 680)
        self.setMinimumSize(1000, 680)

        self.court_model_path = None
        self.court_model = None

        self.create_toolbar()
        self.create_ui()

        # Load default model on startup
        self.load_default_model()

        if self.video_path:
            self.load_video()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def create_toolbar(self):
        toolbar = QToolBar("Tools")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addSeparator()

        # Auto Annotate button - directly connected
        auto_button = QToolButton()
        auto_button.setText("Auto Annotate")
        auto_button.clicked.connect(self.auto_annotate_yolo)
        toolbar.addWidget(auto_button)

        # Add YOLO Config button
        toolbar.addSeparator()
        config_action = QAction("Configuration", self)
        config_action.triggered.connect(self.open_yolo_config)
        toolbar.addAction(config_action)

    def load_default_model(self):
        """Load the default court detection model on startup."""
        if self.db:
            default_model = self.db.get_default_court_model()
            if default_model:
                self.court_model_path = default_model['path']
                # Initialize the model
                if self.initialize_court_model():
                    print(f"Default model loaded: {default_model['name']}")
                else:
                    print("Failed to load default model")
            else:
                print("No default model found in database")

    def open_yolo_config(self):
        """Open the YOLO configuration dialog."""
        dialog = YoloConfigDialog(
            self,
            self.db,
            callback=self.on_model_selected
        )
        dialog.exec()

    def on_model_selected(self, model_path):
        """Callback when a model is selected from the config dialog."""
        self.court_model_path = model_path
        if self.initialize_court_model():
            QMessageBox.information(
                self,
                "Model Loaded",
                "Court detection model has been loaded successfully."
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to load the selected model."
            )

    def initialize_court_model(self):
        """Initialize the court detection model with the configured path."""
        if not self.court_model_path:
            return False

        try:
            from ml_manager.models.CourtSegmentationModule import CourtSegmentationModule
            self.court_model = CourtSegmentationModule(self.court_model_path)
            return True
        except Exception as e:
            print(f"Model initialization error: {e}")
            self.court_model = None
            return False

    def create_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)

        self.view = GraphicsView()
        self.view.setRenderHint(self.view.renderHints())
        layout.addWidget(self.view)
        self.view.setFixedSize(
            self.display_width + 100,
            self.display_height + 50,
        )

        controls = QHBoxLayout()

        self.open_btn = QPushButton("Open Video")
        self.open_btn.setFixedWidth(110)
        self.open_btn.clicked.connect(self.open_video)

        self.frame_spin = QSpinBox()
        self.frame_spin.setFixedWidth(100)
        self.frame_spin.valueChanged.connect(self.change_frame)

        controls.addWidget(self.open_btn)
        controls.addWidget(QLabel("Frame"))
        controls.addWidget(self.frame_spin)
        controls.addStretch()



        save_btn = QPushButton("Submit")
        save_btn.clicked.connect(self.submit)
        controls.addWidget(save_btn)
        layout.addLayout(controls)

    # --------------------------------------------------
    # Video handling
    # --------------------------------------------------

    @staticmethod
    def extract_four_corners(polygon):

        pts = np.array(polygon, dtype=np.float32)

        if len(pts) != 4:
            raise ValueError("Expected exactly 4 polygon points.")

        # Order points: top-left, top-right, bottom-right, bottom-left
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        top_left = pts[np.argmin(s)]
        bottom_right = pts[np.argmax(s)]
        top_right = pts[np.argmin(diff)]
        bottom_left = pts[np.argmax(diff)]

        # Convert to volleyball naming
        return {
            "far_end_line_left": top_left.tolist(),
            "far_end_line_right": top_right.tolist(),
            "near_end_line_left": bottom_left.tolist(),
            "near_end_line_right": bottom_right.tolist(),
        }

    def open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video (*.mp4 *.avi *.mov *.mkv)",
        )

        if path:
            self.video_path = Path(path)
            self.load_video()

    def load_video(self):
        if self.video_path is None:
            return

        cap = cv2.VideoCapture(str(self.video_path))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        self.frame_spin.blockSignals(True)
        self.frame_spin.setMaximum(max(total - 1, 0))

        existing = self.db.load(self.video_path.as_posix())

        if existing:
            self.frame_index = existing.get("frame_index", 0)
        else:
            self.frame_index = 0

        self.frame_spin.setValue(self.frame_index)
        self.frame_spin.blockSignals(False)

        pix = self.read_frame(self.frame_index)

        if pix is None:
            QMessageBox.warning(self, "Error", "Cannot read video frame.")
            return

        if self.scene is None:
            self.scene = CourtScene(pix)
            self.view.setScene(self.scene)

            if existing:
                display_points = {
                    name: [
                        pt[0] / self.scale_x,
                        pt[1] / self.scale_y,
                    ]
                    for name, pt in existing.get("points", {}).items()
                }

                self.scene.load_points(display_points)
        else:
            self.scene.set_background(pix)

    def read_frame(self, index):
        cap = cv2.VideoCapture(str(self.video_path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)

        ok, frame = cap.read()
        cap.release()

        if not ok:
            return None

        self.current_frame = frame.copy()

        original_h, original_w = frame.shape[:2]

        self.scale_x = original_w / self.display_width
        self.scale_y = original_h / self.display_height

        resized = cv2.resize(
            frame,
            (self.display_width, self.display_height),
            interpolation=cv2.INTER_AREA,
        )

        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        image = QImage(
            rgb.data,
            self.display_width,
            self.display_height,
            3 * self.display_width,
            QImage.Format_RGB888,
        )

        return QPixmap.fromImage(image)

    def change_frame(self, value):
        self.frame_index = value

        pix = self.read_frame(value)

        if pix is None:
            return

        if self.scene is None:
            self.scene = CourtScene(pix)
            self.view.setScene(self.scene)
        else:
            self.scene.set_background(pix)

    # --------------------------------------------------
    # Auto annotation
    # --------------------------------------------------

    def auto_annotate_yolo(self):
        """Auto annotate using YOLO models."""
        if self.current_frame is None:
            QMessageBox.warning(self, "Error", "No video frame loaded.")
            return

        # Check if we have a court model configured and loaded
        if not self.court_model_path:
            reply = QMessageBox.question(
                self,
                "Model Not Configured",
                "No court detection model has been configured. Would you like to configure one now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.open_yolo_config()
            return

        # Check if model is initialized
        if self.court_model is None:
            if not self.initialize_court_model():
                return

        # Perform court detection
        try:
            court = self.court_model.segment_court(self.current_frame)

            if court is None:
                QMessageBox.warning(
                    self,
                    "Detection Failed",
                    "Court detection failed. Please ensure the frame contains a volleyball court."
                )
                return

            # Update the scene with detected court corners
            self.scene.set_corner_points(
                {
                    "far_end_line_left": [
                        court.polygon[0][0] / self.scale_x,
                        court.polygon[0][1] / self.scale_y,
                    ],
                    "far_end_line_right": [
                        court.polygon[1][0] / self.scale_x,
                        court.polygon[1][1] / self.scale_y,
                    ],
                    "near_end_line_left": [
                        court.polygon[2][0] / self.scale_x,
                        court.polygon[2][1] / self.scale_y,
                    ],
                    "near_end_line_right": [
                        court.polygon[3][0] / self.scale_x,
                        court.polygon[3][1] / self.scale_y,
                    ],
                }
            )

            QMessageBox.information(
                self,
                "Annotation Complete",
                "Court corners have been automatically annotated."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Detection Error",
                f"Error during court detection:\n{str(e)}"
            )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def submit(self):
        if self.scene is None:
            return

        display_points = self.scene.get_points()

        points = {
            name: [
                pt[0] * self.scale_x,
                pt[1] * self.scale_y,
            ]
            for name, pt in display_points.items()
        }

        if self.video_path is None:
            QMessageBox.warning(
                self,
                "Error",
                "Please enter a new video name.",
            )
            return

        result = {
            "video_name": self.video_path.as_posix(),
            "frame_index": self.frame_index,
            "points": points,
            "court_corners": [
                points["far_end_line_left"],
                points["far_end_line_right"],
                points["near_end_line_right"],
                points["near_end_line_left"],
            ],
            "net_corners": [
                points["net_top_left"],
                points["net_top_right"],
                points["net_bottom_right"],
                points["net_bottom_left"],
            ],
            "polygons": build_polygons(points),
        }

        self.db.save(self.video_path.as_posix(), result)

        self.result = (result, self.video_path)

        self.close()