# using fake dataset first since gesture detection file is not complete

# dependecies installed:
# pip install websockets


import websockets
import asyncio
import json 
import random
import time

# importing from gestures.py
import cv2
from gestures import detect


# ------------------------------
# Global state
# ------------------------------
STATE = {
    "xfader": 0.5,
    "reverb": False,
    "lowpass": False,
}

# Cooldowns (seconds) for one-shot actions
COOLDOWNS = {
    "next_track": 0.8,
    "stop_all": 0.8,
    "resume": 0.8,
    "lowpass_drop": 1.0,
}
_last_fired = {}

# Connected WebSocket clients
CLIENTS = set()


# ------------------------------
# Helpers
# ------------------------------
def can_fire(action: str) -> bool:
    now = time.time()
    last = _last_fired.get(action, 0)
    cd = COOLDOWNS.get(action, 0)
    if now - last >= cd:
        _last_fired[action] = now
        return True
    return False


async def broadcast(msg: dict):
    """Send JSON to all connected WebSocket clients."""
    if not CLIENTS:
        return
    data = json.dumps(msg)
    await asyncio.gather(*[c.send(data) for c in list(CLIENTS)], return_exceptions=True)


def step_xfader(delta: float):
    STATE["xfader"] = max(0.0, min(1.0, STATE["xfader"] + delta))


def map_gesture_to_actions(name: str):
    """Turn a gesture name into one or more actions."""
    if name == "WAVE_UP":
        return [{"type": "action", "name": "next_track"}]
    if name == "WAVE_DOWN":
        return [{"type": "action", "name": "stop_all"}]
    if name == "WAVE_LEFT":
        return [{"type": "action", "name": "crossfader_step", "value": -0.1}]
    if name == "WAVE_RIGHT":
        return [{"type": "action", "name": "crossfader_step", "value": +0.1}]
    if name == "FIST":
        return [{"type": "action", "name": "lowpass_drop"}]
    if name == "OPEN_PALM":
        return [{"type": "action", "name": "reverb_hold"}]
    if name == "SHAKA":
        return [{"type": "action", "name": "resume"}]
    return []


# ------------------------------
# Fake gesture generator
# ------------------------------
async def fake_source():
    gestures = ["FIST","OPEN_PALM","SHAKA","WAVE_UP","WAVE_DOWN","WAVE_LEFT","WAVE_RIGHT"]
    while True:
        yield {"name": random.choice(gestures), "conf": 0.9, "ts": time.time()}
        await asyncio.sleep(1.0)


# ------------------------------
# WebSocket handler
# ------------------------------
async def handle_incoming(ws):
    """Listen for messages from frontend (e.g., invokes)."""
    async for raw in ws:
        try:
            msg = json.loads(raw)
        except:
            continue
        if msg.get("type") == "invoke":
            if msg.get("name") == "toggle_reverb":
                STATE["reverb"] = not STATE["reverb"]
                await broadcast({"type":"action","name":"reverb_toggle","value":STATE["reverb"]})
                await broadcast({"type":"state", **STATE})
            elif msg.get("name") == "set_xfader":
                STATE["xfader"] = float(msg.get("value", 0.5))
                await broadcast({"type":"action","name":"xfader_set","value":STATE["xfader"]})
                await broadcast({"type":"state", **STATE})


async def ws_handler(ws, path):
    CLIENTS.add(ws)
    try:
        await ws.send(json.dumps({"type":"state", **STATE}))
        await handle_incoming(ws)
    finally:
        CLIENTS.discard(ws)


# ------------------------------
# Main loop
# ------------------------------
async def run_loop(source):
    server = await websockets.serve(ws_handler, "localhost", 8765)
    print("WebSocket server running at ws://localhost:8765")

    async for g in source:
        if not g:
            continue
        # Broadcast gesture
        await broadcast({"type":"gesture","name":g["name"],"conf":g["conf"],"ts":g["ts"]})

        # Map to actions
        for act in map_gesture_to_actions(g["name"]):
            name = act["name"]
            if name == "crossfader_step":
                step_xfader(act["value"])
                await broadcast({"type":"action","name":name,"value":act["value"]})
                await broadcast({"type":"state", **STATE})
            elif name == "reverb_hold":
                await broadcast({"type":"action","name":name})
            else:
                if can_fire(name):
                    if name == "lowpass_drop":
                        STATE["lowpass"] = True
                        await broadcast({"type":"action","name":name})
                        await broadcast({"type":"state", **STATE})
                        asyncio.create_task(_release_lowpass())
                    else:
                        await broadcast({"type":"action","name":name})


async def _release_lowpass():
    await asyncio.sleep(1.0)
    STATE["lowpass"] = False
    await broadcast({"type":"action","name":"lowpass_release"})
    await broadcast({"type":"state", **STATE})

#camera source to connect to gestures.py
async def camera_source():
    cap = cv2.VideoCapture(0)
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        results = detect(frame)   
        for r in results:
            # Print detected gestures to console
            print(f"Detected: {r['gesture']} (confidence: {r['conf']:.2f})")
            # normalize output so it matches your expected format
            yield {
                "name": r["gesture"],
                "conf": r["conf"],
                "ts": r["ts"]
            }

        # allow event loop to handle other tasks
        await asyncio.sleep(0)

# ------------------------------
# Entrypoint for testing
# ------------------------------
if __name__ == "__main__":
    asyncio.run(run_loop(camera_source()))

