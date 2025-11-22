# Volleyball Analytics

A compact, end-to-end video analytics pipeline for volleyball that detects game state and objects (ball, set, spike, block, reception), annotates frames, produces an annotated output video and per-frame CSV, and streams real-time processing progress to a web frontend.

- Designed and implemented the backend processing pipeline and WebSocket-based progress reporting.
- Integrated ML models for game-state and action detection and implemented frame annotation and output generation.
- Built the React frontend to show upload and backend processing progress and support automatic/manual download of the processed video.

## Project description

This project processes raw volleyball video to detect game states (PLAY / NO-PLAY / SERVICE) and volleyball-specific objects and actions. A FastAPI backend accepts uploads, runs an ML pipeline (GameState MAE + YOLO-based detectors), annotates frames, and writes an output video and a per-frame CSV for traceability and downstream analysis. Processing progress is streamed to the React frontend over WebSockets so users see upload and processing progress in real time.

## Key features

- Upload video files via the React UI and track upload progress (Axios).
- Real-time backend processing progress via WebSockets.
- ML-based game-state detection and object/action detection (YOLO).
- Annotated output video and per-frame CSV export.
- Background processing with job IDs and a download endpoint for final output.

## Tech stack

- Backend: Python, FastAPI, aiofiles, OpenCV, asyncio, tqdm
- ML: custom GameStateDetector and YOLO-based VolleyBallObjectDetector
- Frontend: React (progress UI, two progress bars per file)
- Deployment: uvicorn (development); designed for containerization / cloud VMs for production

## How it works (concise)

1. User uploads a video → backend saves the file and returns a `job_id`.
2. A background task processes frames in batches and updates job progress via `notify_progress(job_id, percent)`.
3. Frontend opens `ws://.../ws/progress/{job_id}` to receive live updates and display progress.
4. When processing finishes the backend stores the output path and the frontend can download via `/file/download/{job_id}`.

## Quick install & run (dev)

### Backend

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the development server with auto-reload:

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

> If your repo uses a different entrypoint (for example `src/main.py`), run that module instead.

### Frontend

```bash
cd my-react-app
npm install
npm start
```

The React app (Vite) usually serves at `http://localhost:5173` by default.

## Outcome / results

- Stable real-time progress updates during long-running video processing.
- Annotated output video and per-frame CSV that enable downstream analytics and visualization.
- Processes a full volleyball game and splices footage based on Play state to reduce downtime
- Example [edited footage](https://youtu.be/1guT-Q2YAzY) vs [unedited](https://youtu.be/PZltM9uduwk)
