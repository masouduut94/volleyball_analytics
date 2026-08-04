from database import CalibrationDB
from calibration_gui import create_gui

db = CalibrationDB()

result_json, video_name = create_gui(
    video_path=None,
    db_instance=db,
)
