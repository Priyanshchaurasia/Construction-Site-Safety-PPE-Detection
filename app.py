import cv2
import numpy as np
import gradio as gr
import time
from ultralytics import YOLO

from huggingface_hub import hf_hub_download
MODEL_PATH = hf_hub_download(
    repo_id="keremberke/yolov8n-hard-hat-detection",
    filename="best.pt"
)

PPE_CLASSES = {0: "Hardhat", 1: "NO-Hardhat"}
VIOLATION_CLASSES = {1}

model = YOLO(MODEL_PATH)
alerts_log = []
worker_states = {}

WARNING_SECS   = 2.0
VIOLATION_SECS = 5.0
COOLDOWN_SECS  = 30.0


def get_state(worker_id, is_unsafe):
    now = time.time()
    if worker_id not in worker_states:
        worker_states[worker_id] = {"state": "SAFE", "unsafe_since": None, "alert_at": None, "count": 0}
    ws = worker_states[worker_id]
    if not is_unsafe:
        ws["state"] = "SAFE"
        ws["unsafe_since"] = None
        return "SAFE", False
    if ws["unsafe_since"] is None:
        ws["unsafe_since"] = now
    elapsed = now - ws["unsafe_since"]
    cooldown_ok = ws["alert_at"] is None or (now - ws["alert_at"]) >= COOLDOWN_SECS
    if elapsed >= VIOLATION_SECS:
        ws["state"] = "VIOLATION"
        if cooldown_ok:
            ws["alert_at"] = now
            ws["count"] += 1
            return "VIOLATION", True
        return "VIOLATION", False
    elif elapsed >= WARNING_SECS:
        ws["state"] = "WARNING"
    return ws["state"], False


def webcam_frame(frame):
    global alerts_log
    if frame is None:
        return None, "No webcam feed"

    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame_bgr = cv2.resize(frame_bgr, (640, 360))
    results = model.track(frame_bgr, persist=True, verbose=False, conf=0.35, imgsz=320)
    out = frame_bgr.copy()

    if results and results[0].boxes is not None:
        boxes = results[0].boxes
        for i, box in enumerate(boxes):
            cls_id    = int(box.cls[0])
            conf      = float(box.conf[0])
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            worker_id = int(boxes.id[i]) if boxes.id is not None else i
            state, fired = get_state(worker_id, cls_id in VIOLATION_CLASSES)
            if fired:
                alerts_log.append(f"🚨 Worker #{worker_id} — {PPE_CLASSES[cls_id]} [{time.strftime('%H:%M:%S')}]")
                if len(alerts_log) > 20:
                    alerts_log.pop(0)
            color = (0,255,0) if state=="SAFE" else (0,165,255) if state=="WARNING" else (0,0,255)
            cv2.rectangle(out, (x1,y1),(x2,y2), color, 2)
            cv2.putText(out, f"W{worker_id} {PPE_CLASSES.get(cls_id,'?')} {conf:.2f} [{state}]",
                        (x1,y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    out_rgb = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    alert_text = "\n".join(reversed(alerts_log)) if alerts_log else "✅ No violations detected"
    return out_rgb, alert_text


with gr.Blocks(title="⛑️ PPE Safety Monitor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # ⛑️ Construction Site PPE Safety Monitor
    Real-time hardhat detection · YOLOv8 · Violation State Machine (SAFE → WARNING → VIOLATION)
    """)

    with gr.Row():
        cam_input  = gr.Image(sources=["webcam"], streaming=True,
                              label="📷 Camera Feed", scale=1)
        cam_output = gr.Image(label="🔍 Detection Output", scale=1)

    alert_box = gr.Textbox(label="🚨 Violation Log", lines=8, interactive=False,
                           placeholder="Violations will appear here...")

    cam_input.stream(
    fn=webcam_frame,
    inputs=[cam_input],
    outputs=[cam_output, alert_box],
    stream_every=0.1
)

    gr.Markdown("---\n**Repo:** [GitHub](https://github.com/Priyanshchaurasia/Construction_Site_PPE)")

if __name__ == "__main__":
    demo.launch()