# run_time.py
# ------------------------------------------------------------
# Runs Flask video stream + WebSocket + gesture detection
# ------------------------------------------------------------
# Run with: python run_time.py
# Requires:
#   pip install flask flask-cors websockets opencv-python
# ------------------------------------------------------------

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # silence TensorFlow spam

import asyncio
import json
import time
import cv2
import threading
import websockets
from flask import Flask, Response
from flask_cors import CORS
from gestures import detect, state   # your existing detect() + state dict

# ------------------------------------------------------------
# Globals
# ------------------------------------------------------------
CLIENTS = set()
frame_lock = threading.Lock()
output_frame = None

# ------------------------------------------------------------
# Flask setup (video stream)
# ------------------------------------------------------------
app = Flask(__name__)
CORS(app)

@app.route("/video_feed")
def video_feed():
    """Continuously stream MJPEG frames to the web UI."""
    def generate():
        global output_frame
        while True:
            with frame_lock:
                if output_frame is None:
                    continue
                ok, jpeg = cv2.imencode(".jpg", output_frame)
                if not ok:
                    continue
                frame_bytes = jpeg.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

def start_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# ------------------------------------------------------------
# WebSocket setup
# ------------------------------------------------------------
async def broadcast(msg: dict):
    """Send JSON to all connected clients."""
    if not CLIENTS:
        return
    data = json.dumps(msg)
    await asyncio.gather(*[c.send(data) for c in list(CLIENTS)],
                         return_exceptions=True)

async def ws_handler(ws):
    try:
        CLIENTS.add(ws)
        await ws.send(json.dumps({"type": "connected"}))
        async for _ in ws:
            pass
    except Exception as e:
        print(f"⚠️ WebSocket connection error: {e}")
    finally:
        CLIENTS.discard(ws)

async def ws_server():
    async with websockets.serve(ws_handler, "localhost", 8765):
        print("✅ WebSocket server running at ws://localhost:8765")
        await asyncio.Future()

# ------------------------------------------------------------
# Camera + Gesture Detection Loop
# ------------------------------------------------------------
async def camera_loop():
    global output_frame
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 420)

    print("🎥 Camera stream active — resilient dual-hand overlay")

    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            print("⚠️ Camera frame skipped")
            await asyncio.sleep(0.05)
            continue

        frame = cv2.flip(frame, 1)

        try:
            results = detect(frame)
        except Exception as e:
            print(f"⚠️ Detect error: {e}")
            results = []

        # broadcast gesture events
        for r in results:
            await broadcast({
                "type": "gesture",
                "hand": r.get("hand", "Unknown"),
                "gesture": r.get("gesture", "None"),
                "volume": r.get("volume", 0),
                "fingers": r.get("fingers", 0),
                "ts": r.get("ts", time.time())
            })

        # Draw overlays for both hands
        h, w, _ = frame.shape
        left_x = 150
        right_x = w // 2 + 200
        y_base = 150

        if results:
            for r in results:
                hand = r.get("hand", "Unknown")
                x_pos = left_x if hand == "Left" else right_x
                y = y_base

                # translucent box
                overlay = frame.copy()
                cv2.rectangle(overlay, (x_pos - 20, y - 40),
                              (x_pos + 450, y + 130), (0, 0, 0), -1)
                frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

                # text + bars
                gesture_text = r.get("gesture", "None")
                fingers = r.get("fingers", 0)
                vol = r.get("volume", 0)

                cv2.putText(frame, f"{hand}: {gesture_text}",
                            (x_pos, y),
                            cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)
                cv2.putText(frame, f"Fingers: {fingers}  |  Vol: {vol}",
                            (x_pos, y + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

                # volume bar
                bar_x = x_pos
                bar_y = h - 150
                vol_height = int((vol / 100) * 300)
                cv2.rectangle(frame, (bar_x, bar_y - vol_height),
                              (bar_x + 60, bar_y), (0, 255, 0), -1)
                cv2.rectangle(frame, (bar_x, bar_y - 300),
                              (bar_x + 60, bar_y), (255, 255, 255), 3)

                # wave info
                wave_info = state.get(hand, {}).get("last_wave", {})
                if time.time() - wave_info.get("time", 0) < 1.5:
                    cv2.putText(frame, wave_info.get("text", ""),
                                (x_pos, bar_y - 350),
                                cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 255), 3)
        else:
            # show fallback when no hands detected
            cv2.putText(frame, "No hands detected",
                        (int(w / 2) - 200, int(h / 2)),
                        cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)

        # push frame to stream (always!)
        with frame_lock:
            output_frame = frame.copy()

        await asyncio.sleep(0.05)

    cap.release()

# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------
async def main():
    threading.Thread(target=start_flask, daemon=True).start()
    await asyncio.gather(ws_server(), camera_loop())

if __name__ == "__main__":
    asyncio.run(main())
