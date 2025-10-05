# backend/run_time.py
import asyncio
import json
import time
import websockets
from jamendo_player import JamendoPlayer
from gestures import detect_async  # ✅ only import the async webcam loop

STATE = {"xfader": 0.5, "reverb": False, "lowpass": False}
COOLDOWNS = {"next_track": 0.8, "stop_all": 0.8, "resume": 0.8, "lowpass_drop": 1.0}
_last_fired, CLIENTS = {}, set()


def can_fire(action: str):
    now = time.time()
    last = _last_fired.get(action, 0)
    if now - last >= COOLDOWNS.get(action, 0):
        _last_fired[action] = now
        return True
    return False


async def broadcast(msg: dict):
    if CLIENTS:
        data = json.dumps(msg)
        await asyncio.gather(*[c.send(data) for c in list(CLIENTS)], return_exceptions=True)


def step_xfader(delta: float):
    STATE["xfader"] = max(0.0, min(1.0, STATE["xfader"] + delta))


def map_gesture_to_actions(name: str):
    name = name.upper()
    if "WAVE_UP" in name: return [{"type": "action", "name": "next_track"}]
    if "WAVE_DOWN" in name: return [{"type": "action", "name": "stop_all"}]
    if "WAVE_LEFT" in name: return [{"type": "action", "name": "crossfader_step", "value": -0.1}]
    if "WAVE_RIGHT" in name: return [{"type": "action", "name": "crossfader_step", "value": +0.1}]
    if "FIST" in name: return [{"type": "action", "name": "lowpass_drop"}]
    if "OPEN_PALM" in name: return [{"type": "action", "name": "reverb_hold"}]
    if "SHAKA" in name: return [{"type": "action", "name": "resume"}]
    return []


async def ws_handler(ws):
    CLIENTS.add(ws)
    try:
        await ws.send(json.dumps({"type": "state", **STATE}))
        async for _ in ws:
            pass
    finally:
        CLIENTS.discard(ws)


async def _release_lowpass():
    await asyncio.sleep(1.0)
    STATE["lowpass"] = False
    await broadcast({"type": "action", "name": "lowpass_release"})
    await broadcast({"type": "state", **STATE})


async def run_loop(source):
    player = JamendoPlayer()
    await websockets.serve(ws_handler, "localhost", 8765)
    print("✅ WebSocket server running at ws://localhost:8765")

    async for g in source:
        if not g:
            continue

        await broadcast({"type": "gesture", **g})
        for act in map_gesture_to_actions(g["gesture"]):
            n = act["name"]
            if n == "crossfader_step":
                step_xfader(act["value"])
                await broadcast({"type": "state", **STATE})
            elif can_fire(n):
                if n == "next_track": player.stop(); player.play_next()
                elif n == "stop_all": player.stop()
                elif n == "resume": player.resume()
                elif n == "lowpass_drop":
                    STATE["lowpass"] = True
                    await broadcast({"type": "state", **STATE})
                    asyncio.create_task(_release_lowpass())


if __name__ == "__main__":
    print("🚀 Starting AirDJ Runtime (Webcam Mode)...")
    asyncio.run(run_loop(detect_async()))  # ✅ directly uses the one from gestures.py
