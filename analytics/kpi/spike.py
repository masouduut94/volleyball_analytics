from src.backend.app.api_interface import APIInterface
from src.backend.app.schemas import rallies
import cv2
import matplotlib.pyplot as plt
from os.path import join
from pathlib import Path

if __name__ == '__main__':
    api = APIInterface("http://localhost:8000")
    # p = api.get_rallies(match_id=1)
    t = api.get_rallies(match_id=1)
    print(t)
