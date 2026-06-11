import sqlite3
from datetime import datetime
import asyncio
import cv2
import base64
import time
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from src.detector import PPEDetector
app = FastAPI(title="PPE Safety Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

detector = PPEDetector()          # loads yolov8n.pt
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect("violations.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            violation TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def log_violation(worker_id, violation):
    conn = sqlite3.connect("violations.db")
    conn.execute("INSERT INTO violations VALUES (NULL,?,?,?)",
                 (worker_id, violation, datetime.now().isoformat()))
    conn.commit()
    conn.close()

current_video_path = None         # set after upload


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    global current_video_path
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        f.write(await file.read())
    current_video_path = str(dest)
    return {"filename": file.filename, "path": current_video_path}


@app.get("/stats")
def get_stats():
    return detector.get_stats()


@app.get("/alerts")
def get_alerts():
    return detector.alerts

@app.get("/violations/log")
def violations_log():
    conn = sqlite3.connect("violations.db")
    rows = conn.execute("SELECT * FROM violations ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return [{"id": r[0], "worker_id": r[1], "violation": r[2], "timestamp": r[3]} for r in rows]

@app.websocket("/ws/stream")
async def stream(websocket: WebSocket):
    await websocket.accept()
    global current_video_path

    if not current_video_path:
        await websocket.send_json({"error": "No video uploaded yet"})
        await websocket.close()
        return

    cap = cv2.VideoCapture(current_video_path)
    if not cap.isOpened():
        await websocket.send_json({"error": "Cannot open video"})
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)   # loop video
                continue

            # Resize for speed on CPU
            frame = cv2.resize(frame, (480, 270))
            annotated = detector.process_frame(frame)

            _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])
            b64 = base64.b64encode(buf).decode("utf-8")

            await websocket.send_json({
                "frame": b64,
                "stats": detector.get_stats()
            })
            await asyncio.sleep(0.04)   # ~25 FPS cap

    except WebSocketDisconnect:
        pass
    finally:
        cap.release()


# Serve React frontend
if Path("frontend/dist").exists():
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)