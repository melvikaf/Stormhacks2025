// src/pages/TestPage.jsx
import { useEffect, useState } from "react";

export default function TestPage() {
  const [status, setStatus] = useState("Connecting...");
  const [lastMsg, setLastMsg] = useState("");

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => setStatus("✅ Connected to backend");
    ws.onclose = () => setStatus("❌ Disconnected");
    ws.onerror = (err) => setStatus("⚠️ Error: " + err.message);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMsg(JSON.stringify(data, null, 2));
      } catch {
        setLastMsg(event.data);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{
      background: "#111",
      color: "#fff",
      height: "100vh",
      padding: "2rem",
      fontFamily: "monospace"
    }}>
      <h2>🧠 Test WebSocket Connection</h2>
      <p>{status}</p>
      <pre style={{
        marginTop: "2rem",
        background: "#222",
        padding: "1rem",
        borderRadius: "8px",
        overflowX: "auto"
      }}>
        {lastMsg || "Waiting for messages..."}
      </pre>
    </div>
  );
}

