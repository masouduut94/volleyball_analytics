import sys
from PySide6.QtWidgets import QApplication
from .window import CalibrationWindow

def create_gui(video_path: str = None, db_instance=None):
    app = QApplication.instance()
    owns = app is None
    if owns:
        app = QApplication(sys.argv)

    window = CalibrationWindow(video_path, db_instance)
    window.show()

    if owns:
        app.exec()
    else:
        loop = app.exec()

    return window.result