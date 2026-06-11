from src.detector import WorkerState, STATE_SAFE, STATE_WARNING, STATE_VIOLATION
import time

def test_worker_starts_safe():
    ws = WorkerState(1)
    assert ws.state == STATE_SAFE

def test_worker_stays_safe_when_no_violation():
    ws = WorkerState(2)
    for _ in range(10):
        ws.update(False)
    assert ws.state == STATE_SAFE

def test_violation_count_increments():
    ws = WorkerState(3)
    ws.unsafe_since = time.time() - 10   # simulate 10s of unsafe
    ws.update(True)
    assert ws.violation_count == 1