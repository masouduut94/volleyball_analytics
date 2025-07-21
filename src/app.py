from fastapi import FastAPI, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import cv2
import yaml
from tqdm import tqdm
from time import time
from os import makedirs
from os.path import join
from pathlib import Path
from argparse import ArgumentParser
import csv
import aiofiles

from src.utilities.utils import ProjectLogger
from src.backend.app.enums.enums import GameState
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector

app = FastAPI()
app.add_middleware(
    CORSMiddleware
    , allow_origins=["*"]
    , allow_credentials=True
    , allow_methods=["*"]
    , allow_headers=["*"]
)
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/file/uploadAndProcess")
async def upload_file(file: UploadFile):
    # TODO: Add exception handling for file upload
    model_cfg = 'conf/ml_models.yaml'
    setup_cfg = 'conf/setup.yaml'
    output_path = "runs/DEMO"
    buffer_size = 30
    UPLOAD_DIR = "data/videos/"
    # with open(file.filename, "wb") as f:
    #     f.write(file.file.read())
    # Ensure upload directory exists
    makedirs(UPLOAD_DIR, exist_ok=True)

    save_to = join(UPLOAD_DIR, file.filename)

    try:
        # Read and write file asynchronously
        async with aiofiles.open(save_to, "wb") as out_file:
            while content := await file.read(buffer_size * 1024):
                await out_file.write(content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    logger = ProjectLogger(filename="logs.log")

    video_path = Path(file.filename)
    output_path = Path(output_path)

    model_cfg: dict = yaml.load(open(model_cfg), Loader=yaml.SafeLoader)
    setup_cfg: dict = yaml.load(open(setup_cfg), Loader=yaml.SafeLoader)

    model_cfg.update(setup_cfg)
    logger.info("Configs initialized successfully.")
    state_detector = GameStateDetector(cfg=model_cfg['video_mae']['game_state_3'])
    vb_object_detector = VolleyBallObjectDetector(
        model_cfg,
        use_player_detection=True,
        video_name=video_path.name
    )
    logger.info("Yolo detector initialized.")
    cap = cv2.VideoCapture(video_path.as_posix())
    assert video_path.is_file(), logger.info(f'file {video_path.as_posix()} not found...')
    assert cap.isOpened(), logger.info(f'the video file is not opening {video_path}')
    makedirs(output_path, exist_ok=True)

    status = True
    buffer = []
    fno_buffer = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    pbar = tqdm(total=n_frames, desc=f'writing 0/{n_frames}')
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    output_name = join(output_path, f'{Path(video_path).stem}_DEMO.mp4')
    writer = cv2.VideoWriter(output_name, codec, fps, (w, h))
    logger.success("Process initialization completed...")
    game_state_per_frame = []

    while status:
        status, frame = cap.read()
        fno = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if not status:
            break

        pbar.update(1)
        buffer.append(frame)
        fno_buffer.append(fno)

        if len(buffer) != buffer_size:
            continue

        t1 = time()
        label = state_detector.predict(buffer)
        match label:
            case GameState.SERVICE:
                color = (0, 255, 0)
            case GameState.NO_PLAY:
                color = (0, 0, 255)
            case GameState.PLAY:
                color = (255, 255, 0)
            case _:
                color = (255, 255, 255)

        for i, f in enumerate(buffer):
            game_state = state_detector.state2label[label].upper()
            frame_info = f"Frame #{fno_buffer[i]}/{n_frames}".upper()

            buffer[i] = cv2.putText(buffer[i], f"Game Status: {game_state}", (150, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 2)
            buffer[i] = cv2.putText(buffer[i], frame_info, (w - 350, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (255, 0, 0), 2)

            if label != GameState.NO_PLAY:
                # YOLO Object detection
                balls = vb_object_detector.detect_balls(f)
                vb_objects = vb_object_detector.detect_actions(f, exclude=('ball',))
                blocks = vb_objects['block']
                sets = vb_objects['set']
                spikes = vb_objects['spike']
                receives = vb_objects['receive']
                services = vb_objects['serve']
                objects = balls + blocks + sets + receives + spikes + services
                # logger.info(f"Detected {len(objects)} objects...")
                buffer[i] = vb_object_detector.draw_bboxes(buffer[i], objects)
            game_state_per_frame.append({
                "frame": fno_buffer[i],
                "game_state": game_state
            })
            writer.write(buffer[i])

        

        t2 = time()
        pbar.set_description(f'processing {fno}/{n_frames} | process time: {abs(t2 - t1): .3f}')

        buffer.clear()
        fno_buffer.clear()
    logger.success(f"Process finished. Saved output as {output_name}. ")
    with open(f'{Path(video_path).stem}_DEMO.csv', "w", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=["frame", "game_state"])
        csv_writer.writeheader()
        csv_writer.writerows(game_state_per_frame)
    writer.release()
    cap.release()
    pbar.close()
    # return {"filename": file.filename}
    return FileResponse(path=output_name,media_type='video/mp4', filename=output_name)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)