import { useEffect, useState, useRef } from "react";

function App() {
  const [connected, setConnected] = useState(false);
  const [gesture, setGesture] = useState("—");
  const [track, setTrack] = useState("No track playing");
  const [state, setState] = useState({
    xfader: 0.5,
    reverb: false,
    lowpass: false,
  });

  const wsRef = useRef(null);

  // ----------------------------
  // WebSocket Connection
  // ----------------------------
  useEffect(() => {
    let ws;
    let retryTimeout;

    const connect = () => {
      ws = new WebSocket("ws://localhost:8765");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("✅ Connected to Air DJ backend");
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          console.log("📨 From backend:", msg);

          // Handle message types
          if (msg.type === "gesture") {
            setGesture(msg.name || "—");
          } else if (msg.type === "action") {
            if (msg.name === "next_track") setTrack("🎵 New track playing...");
            if (msg.name === "stop_all") setTrack("⏹️ Stopped");
            if (msg.name === "resume") setTrack("▶️ Resumed");
          } else if (msg.type === "state") {
            setState({
              xfader: msg.xfader ?? 0.5,
              reverb: msg.reverb ?? false,
              lowpass: msg.lowpass ?? false,
            });
          }
        } catch (err) {
          console.warn("⚠️ Failed to parse message:", event.data);
        }
      };

      ws.onclose = () => {
        console.warn("❌ Disconnected from backend");
        setConnected(false);

        // Try reconnecting after a delay
        retryTimeout = setTimeout(() => {
          console.log("🔁 Retrying WebSocket connection...");
          connect();
        }, 3000);
      };

      ws.onerror = (err) => {
        console.error("⚠️ WebSocket error:", err);
        ws.close();
      };
    };

    connect();

    // Cleanup
    return () => {
      if (retryTimeout) clearTimeout(retryTimeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // ----------------------------
  // Render UI
  // ----------------------------
  return (
    <div
      style={{
        height: "100vh",
        background: "linear-gradient(135deg, #111 0%, #222 100%)",
        color: "white",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Poppins, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>🎧 Air DJ</h1>

      <p
        style={{
          fontSize: "1.2rem",
          color: connected ? "#0f0" : "#f33",
          marginBottom: "1.5rem",
        }}
      >
        {connected ? "🟢 Connected to Backend" : "🔴 Not Connected"}
      </p>

      <div
        style={{
          background: "#333",
          padding: "1.5rem 2rem",
          borderRadius: "1rem",
          textAlign: "center",
          boxShadow: "0 0 15px rgba(255,255,255,0.1)",
          minWidth: "320px",
        }}
      >
        <h2 style={{ fontSize: "1.8rem" }}>Current Gesture</h2>
        <p style={{ fontSize: "2rem", color: "#4fc3f7" }}>{gesture}</p>

        <h3 style={{ marginTop: "1rem", fontSize: "1.5rem" }}>Now Playing</h3>
        <p style={{ fontSize: "1.2rem", color: "#a5d6a7" }}>{track}</p>

        <h3 style={{ marginTop: "1rem" }}>State</h3>
        <p>🎚️ Crossfader: {(state.xfader * 100).toFixed(0)}%</p>
        <p>🌊 Reverb: {state.reverb ? "ON" : "OFF"}</p>
        <p>🎚 Lowpass: {state.lowpass ? "ON" : "OFF"}</p>
      </div>

      <p style={{ marginTop: "3rem", opacity: 0.7 }}>
        Try waving your hand, making a fist, or showing a shaka 🤙
      </p>
    </div>
  );
}

export default App;
