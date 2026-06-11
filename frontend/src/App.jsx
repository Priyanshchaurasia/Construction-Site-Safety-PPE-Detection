import { useState, useEffect, useRef } from "react";

const WS_URL = "ws://localhost:8000/ws/stream";
const API_URL = "http://localhost:8000";

const STATE_COLORS = {
  SAFE: "#22c55e",
  WARNING: "#f97316",
  VIOLATION: "#ef4444",
};

export default function App() {
  const [connected, setConnected] = useState(false);
  const [frame, setFrame] = useState(null);
  const [stats, setStats] = useState({ total_workers_seen: 0, total_alerts: 0, fps: 0, recent_alerts: [] });
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [streaming, setStreaming] = useState(false);
  const wsRef = useRef(null);

  const uploadVideo = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    await fetch(`${API_URL}/upload`, { method: "POST", body: form });
    setUploadedFile(file.name);
    setUploading(false);
  };

  const startStream = () => {
    if (wsRef.current) wsRef.current.close();
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => { setConnected(true); setStreaming(true); };
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.frame) setFrame("data:image/jpeg;base64," + data.frame);
      if (data.stats) setStats(data.stats);
    };
    ws.onclose = () => { setConnected(false); setStreaming(false); };
    wsRef.current = ws;
  };

  const stopStream = () => {
    wsRef.current?.close();
    setStreaming(false);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#f1f5f9", fontFamily: "system-ui, sans-serif", padding: "24px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "22px", fontWeight: 700, color: "#f8fafc" }}>⛑️ Construction Safety Monitor</h1>
          <p style={{ margin: "4px 0 0", fontSize: "13px", color: "#94a3b8" }}>Real-time PPE violation detection · YOLOv8 + ByteTrack</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: connected ? "#22c55e" : "#ef4444" }} />
          <span style={{ fontSize: "13px", color: "#94a3b8" }}>{connected ? "Live" : "Disconnected"}</span>
        </div>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "20px" }}>
        {[
          { label: "Workers Tracked", value: stats.total_workers_seen, color: "#3b82f6" },
          { label: "Total Alerts", value: stats.total_alerts, color: "#ef4444" },
          { label: "FPS", value: stats.fps, color: "#22c55e" },
        ].map((s) => (
          <div key={s.label} style={{ background: "#1e293b", borderRadius: "12px", padding: "16px 20px", border: "1px solid #334155" }}>
            <p style={{ margin: "0 0 6px", fontSize: "12px", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em" }}>{s.label}</p>
            <p style={{ margin: 0, fontSize: "28px", fontWeight: 700, color: s.color }}>{s.value}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: "16px" }}>
        {/* Video panel */}
        <div style={{ background: "#1e293b", borderRadius: "12px", border: "1px solid #334155", overflow: "hidden" }}>
          <div style={{ padding: "14px 18px", borderBottom: "1px solid #334155", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "14px", fontWeight: 600 }}>Live Feed</span>
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <label style={{ cursor: "pointer", background: "#334155", border: "none", color: "#f1f5f9", padding: "6px 14px", borderRadius: "8px", fontSize: "13px" }}>
                {uploading ? "Uploading..." : uploadedFile ? `📁 ${uploadedFile}` : "📂 Upload Video"}
                <input type="file" accept="video/*" style={{ display: "none" }} onChange={uploadVideo} />
              </label>
              {!streaming ? (
                <button onClick={startStream} disabled={!uploadedFile}
                  style={{ background: uploadedFile ? "#22c55e" : "#334155", border: "none", color: "#fff", padding: "6px 16px", borderRadius: "8px", fontSize: "13px", cursor: uploadedFile ? "pointer" : "not-allowed" }}>
                  ▶ Start
                </button>
              ) : (
                <button onClick={stopStream}
                  style={{ background: "#ef4444", border: "none", color: "#fff", padding: "6px 16px", borderRadius: "8px", fontSize: "13px", cursor: "pointer" }}>
                  ⏹ Stop
                </button>
              )}
            </div>
          </div>
          <div style={{ background: "#0f172a", minHeight: "360px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            {frame
              ? <img src={frame} style={{ width: "100%", display: "block" }} alt="stream" />
              : <div style={{ textAlign: "center", color: "#475569" }}>
                  <p style={{ fontSize: "48px", margin: "0 0 8px" }}>🎥</p>
                  <p style={{ fontSize: "14px" }}>Upload a video and press Start</p>
                </div>
            }
          </div>
        </div>

        {/* Alerts panel */}
        <div style={{ background: "#1e293b", borderRadius: "12px", border: "1px solid #334155", display: "flex", flexDirection: "column" }}>
          <div style={{ padding: "14px 18px", borderBottom: "1px solid #334155" }}>
            <span style={{ fontSize: "14px", fontWeight: 600 }}>🚨 Recent Alerts</span>
          </div>
          <div style={{ flex: 1, overflowY: "auto", padding: "10px" }}>
            {stats.recent_alerts.length === 0
              ? <p style={{ color: "#475569", fontSize: "13px", textAlign: "center", marginTop: "40px" }}>No violations detected</p>
              : [...stats.recent_alerts].reverse().map((a, i) => (
                <div key={i} style={{ background: "#0f172a", borderRadius: "8px", padding: "10px 12px", marginBottom: "8px", borderLeft: "3px solid #ef4444" }}>
                  <p style={{ margin: "0 0 2px", fontSize: "13px", fontWeight: 600, color: "#f87171" }}>Worker #{a.worker_id}</p>
                  <p style={{ margin: "0 0 2px", fontSize: "12px", color: "#94a3b8" }}>{a.violation}</p>
                  <p style={{ margin: 0, fontSize: "11px", color: "#475569" }}>{a.timestamp} · Alert #{a.count}</p>
                </div>
              ))
            }
          </div>
        </div>
      </div>
    </div>
  );
}