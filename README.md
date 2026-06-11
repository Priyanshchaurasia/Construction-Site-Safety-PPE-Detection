# ⛑️ Construction Site Safety Monitor

Real-time PPE violation detection system built with YOLOv8, FastAPI, React, and Docker.

## Features
- Real-time hardhat detection at 8–12 FPS on CPU
- Persistent worker tracking with ByteTrack-style IDs
- Violation state machine: WARNING (2s) → VIOLATION (5s) → Alert
- SQLite violation log with REST API
- React dashboard with live annotated video feed
- Dockerized with GitHub Actions CI/CD

## Tech Stack
`YOLOv8` `FastAPI` `WebSocket` `React` `Vite` `Docker` `SQLite` `GitHub Actions`

## Run Locally

```bash
# Backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker build -t ppe-safety-monitor .
docker run -p 8000:8000 ppe-safety-monitor
```

## Resume Bullet
> Built and deployed a real-time construction safety monitoring platform using YOLOv8, FastAPI, React, and Docker that tracked workers across video streams and detected PPE violations. Engineered a violation state machine that reduced false-positive alerts by eliminating single-frame detections, and deployed via a GitHub Actions CI/CD pipeline.