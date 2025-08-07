from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import aiofiles
import asyncio
import cv2
import yaml
from tqdm import tqdm
from os import makedirs
from os.path import join
from pathlib import Path
import csv
from time import time

from src.utilities.utils import ProjectLogger
from src.backend.app.enums.enums import GameState
from src.ml.video_mae.game_state.gamestate_detection import GameStateDetector
from src.ml.yolo.volleyball_object_detector import VolleyBallObjectDetector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = set()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Keeps the connection open
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def notify_progress(p):
    for client in connected_clients.copy():
        try:
            await client.send_text(str(p))
        except:
            connected_clients.remove(client)

@app.post("/file/uploadAndProcess")
async def upload_file(file: UploadFile):
    UPLOAD_DIR = "data/videos/"
    makedirs(UPLOAD_DIR, exist_ok=True)
    save_to = join(UPLOAD_DIR, file.filename)

    try:
        async with aiofiles.open(save_to, "wb") as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # Start background video processing
    asyncio.create_task(process_video_in_background(save_to))

    return {"status": "processing started"}

async def process_video_in_background(video_path_str: str):
    model_cfg_path = 'conf/ml_models.yaml'
    setup_cfg_path = 'conf/setup.yaml'
    output_path = "runs/DEMO"
    buffer_size = 30

    logger = ProjectLogger(filename="logs.log")

    video_path = Path(video_path_str)
    output_path = Path(output_path)

    model_cfg = yaml.load(open(model_cfg_path), Loader=yaml.SafeLoader)
    setup_cfg = yaml.load(open(setup_cfg_path), Loader=yaml.SafeLoader)
    model_cfg.update(setup_cfg)

    logger.info("Configs initialized successfully.")

    state_detector = GameStateDetector(cfg=model_cfg['video_mae']['game_state_3'])
    vb_object_detector = VolleyBallObjectDetector(
        model_cfg,
        use_player_detection=True,
        video_name=video_path.name
    )
    logger.info("YOLO detector initialized.")

    cap = cv2.VideoCapture(video_path.as_posix())
    assert cap.isOpened(), logger.error(f"Cannot open video: {video_path}")

    makedirs(output_path, exist_ok=True)

    buffer = []
    fno_buffer = []
    w, h, fps, _, n_frames = [int(cap.get(i)) for i in range(3, 8)]
    pbar = tqdm(total=n_frames, desc=f'Processing 0/{n_frames}')
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    output_name = join(output_path, f'{video_path.stem}_DEMO.mp4')
    writer = cv2.VideoWriter(output_name, codec, fps, (w, h))
    game_state_per_frame = []

    while True:
        status, frame = cap.read()
        if not status:
            break

        fno = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        progress = round((fno / n_frames) * 100)
        await notify_progress(progress)  # Send update
        await asyncio.sleep(0)  # Let event loop breathe

        pbar.update(1)
        buffer.append(frame)
        fno_buffer.append(fno)

        if len(buffer) != buffer_size:
            continue


        t1 = time()
        label = state_detector.predict(buffer)

        color = {
            GameState.SERVICE: (0, 255, 0),
            GameState.NO_PLAY: (0, 0, 255),
            GameState.PLAY: (255, 255, 0),
        }.get(label, (255, 255, 255))

        for i, f in enumerate(buffer):
            game_state = state_detector.state2label[label].upper()
            frame_info = f"Frame #{fno_buffer[i]}/{n_frames}".upper()

            buffer[i] = cv2.putText(buffer[i], f"Game Status: {game_state}", (150, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 2)
            buffer[i] = cv2.putText(buffer[i], frame_info, (w - 350, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            if label != GameState.NO_PLAY:
                balls = vb_object_detector.detect_balls(f)
                vb_objects = vb_object_detector.detect_actions(f, exclude=('ball',))
                objects = (
                    balls +
                    vb_objects['block'] +
                    vb_objects['set'] +
                    vb_objects['receive'] +
                    vb_objects['spike'] +
                    vb_objects['serve']
                )
                buffer[i] = vb_object_detector.draw_bboxes(buffer[i], objects)

            game_state_per_frame.append({
                "frame": fno_buffer[i],
                "game_state": game_state
            })
            writer.write(buffer[i])

        t2 = time()
        pbar.set_description(f'Processed {fno}/{n_frames} | {t2 - t1:.2f}s')
        buffer.clear()
        fno_buffer.clear()

    cap.release()
    writer.release()
    pbar.close()

    logger.success(f"Finished processing. Output saved to: {output_name}")

    with open(f'{video_path.stem}_DEMO.csv', "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["frame", "game_state"])
        writer.writeheader()
        writer.writerows(game_state_per_frame)

    await notify_progress(100)  # Final update

