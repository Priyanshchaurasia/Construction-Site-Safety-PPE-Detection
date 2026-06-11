import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import time

PPE_CLASSES = {
    0: "Hardhat",
    1: "NO-Hardhat",
}

VIOLATION_CLASSES = {1}   # NO-Hardhat
SAFE_CLASSES      = {0}   # Hardhat    # Hardhat, Mask, Safety Vest

# State machine states
STATE_SAFE      = "SAFE"
STATE_WARNING   = "WARNING"
STATE_VIOLATION = "VIOLATION"

WARNING_SECS  = 2.0
VIOLATION_SECS = 5.0
COOLDOWN_SECS  = 30.0


class WorkerState:
    def __init__(self, worker_id):
        self.worker_id   = worker_id
        self.state       = STATE_SAFE
        self.unsafe_since = None
        self.alert_sent_at = None
        self.violation_count = 0
        self.last_seen   = time.time()

    def update(self, is_unsafe: bool):
        now = time.time()
        self.last_seen = now

        if not is_unsafe:
            self.state = STATE_SAFE
            self.unsafe_since = None
            return False   # no alert

        # unsafe frame
        if self.unsafe_since is None:
            self.unsafe_since = now

        elapsed = now - self.unsafe_since

        # cooldown check
        if self.alert_sent_at and (now - self.alert_sent_at) < COOLDOWN_SECS:
            self.state = STATE_VIOLATION
            return False

        if elapsed >= VIOLATION_SECS:
            self.state = STATE_VIOLATION
            if self.alert_sent_at is None or (now - self.alert_sent_at) >= COOLDOWN_SECS:
                self.alert_sent_at = now
                self.violation_count += 1
                return True   # fire alert
        elif elapsed >= WARNING_SECS:
            self.state = STATE_WARNING

        return False


class PPEDetector:
    def __init__(self, model_path=r"C:\Users\priya\.cache\huggingface\hub\models--keremberke--yolov8n-hard-hat-detection\snapshots\287bafa2feb311ee45d21f9e9b33315ff6ff955d\best.pt"):
        # Will auto-download yolov8n.pt on first run
        self.model = YOLO(model_path)
        self.worker_states: dict[int, WorkerState] = {}
        self.track_history  = defaultdict(list)
        self.alerts = []          # list of alert dicts
        self.frame_count = 0
        self.fps_start   = time.time()
        self.fps         = 0.0

    def _get_or_create(self, worker_id) -> WorkerState:
        if worker_id not in self.worker_states:
            self.worker_states[worker_id] = WorkerState(worker_id)
        return self.worker_states[worker_id]

    def process_frame(self, frame: np.ndarray):
        self.frame_count += 1
        elapsed = time.time() - self.fps_start
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start = time.time()

        results = self.model.track(frame, persist=True, verbose=False,
                           conf=0.35, iou=0.45, imgsz=320)
        annotated = frame.copy()
        active_ids = set()

        if results and results[0].boxes is not None:
            boxes   = results[0].boxes
            has_ids = boxes.id is not None

            for i, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                conf   = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                worker_id = int(boxes.id[i]) if has_ids else i
                active_ids.add(worker_id)

                is_unsafe = cls_id in VIOLATION_CLASSES
                ws = self._get_or_create(worker_id)
                fired = ws.update(is_unsafe)

                if fired:
                    alert = {
                        "worker_id": worker_id,
                        "violation": PPE_CLASSES.get(cls_id, "Unknown"),
                        "timestamp": time.strftime("%H:%M:%S"),
                        "count": ws.violation_count
                    }
                    self.alerts.append(alert)
                    if len(self.alerts) > 50:
                        self.alerts.pop(0)

                # Color by state
                state = ws.state
                color = (0, 255, 0)   # green = SAFE
                if state == STATE_WARNING:   color = (0, 165, 255)  # orange
                if state == STATE_VIOLATION: color = (0, 0, 255)    # red

                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                label = f"W{worker_id} {PPE_CLASSES.get(cls_id,'?')} {conf:.2f}"
                cv2.putText(annotated, label, (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # State badge
                cv2.putText(annotated, state, (x1, y2 + 16),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        # FPS overlay
        cv2.putText(annotated, f"FPS: {self.fps:.1f}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Violation counter
        total_v = sum(ws.violation_count for ws in self.worker_states.values())
        cv2.putText(annotated, f"Alerts: {total_v}", (10, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return annotated

    def get_stats(self):
        return {
            "total_workers_seen": len(self.worker_states),
            "total_alerts": sum(ws.violation_count for ws in self.worker_states.values()),
            "fps": round(self.fps, 1),
            "recent_alerts": self.alerts[-10:]
        }