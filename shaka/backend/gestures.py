import cv2
import time
import numpy as np
import mediapipe as mp
from collections import deque
import mido
from mido import Message

# ------------------------------------------------------------
# MIDI setup
# ------------------------------------------------------------
try:
    outport = mido.open_output('shaka 1')
except IOError:
    outport = mido.open_output('shaka')

def send_midi_note(hand, note, velocity=100):
    msg = Message('note_on', note=note, velocity=velocity, channel=0 if hand == "Left" else 1)
    outport.send(msg)

def send_midi_cc(hand, control, value):
    msg = Message('control_change', control=control, value=int(value),
                  channel=0 if hand == "Left" else 1)
    outport.send(msg)

# ------------------------------------------------------------
# Mediapipe setup
# ------------------------------------------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

left_hist = deque(maxlen=5)
right_hist = deque(maxlen=5)

mirror_flip = True  # flip directions if your webcam mirrors the image

state = {
    "Left": {"volume": 50, "prev_volume": 50, "last_swipe": {"text": "", "time": 0, "dir": None}},
    "Right": {"volume": 50, "prev_volume": 50, "last_swipe": {"text": "", "time": 0, "dir": None}},
}

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def get_finger_states(pts, label):
    states = {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0}
    if label == "Right":
        states["thumb"] = int(pts[4][0] > pts[3][0])
    else:
        states["thumb"] = int(pts[4][0] < pts[3][0])
    for name, tip, mid in zip(["index", "middle", "ring", "pinky"],
                              [8, 12, 16, 20], [6, 10, 14, 18]):
        states[name] = int(pts[tip][1] < pts[mid][1])
    return states


def classify_hand_state(label, pts):
    wrist = pts[0]
    fingers = get_finger_states(pts[:, :2], label)
    up_count = sum(fingers.values())
    gesture = "UNKNOWN"

    if up_count == 0:
        gesture = "FIST"
    elif up_count == 5:
        gesture = "OPEN_PALM"
    elif fingers["thumb"] and fingers["pinky"] and not any([fingers["index"], fingers["middle"], fingers["ring"]]):
        gesture = "SHAKA"
    elif fingers["index"] and fingers["middle"] and not any([fingers["thumb"], fingers["ring"], fingers["pinky"]]):
        gesture = "PEACE"
    elif up_count == 1 and fingers["index"]:
        gesture = "ONE_FINGER"
    else:
        gesture = f"{up_count}_FINGERS"

    hist = left_hist if label == "Left" else right_hist
    hist.append(wrist)

    dx, dy, dz = 0, 0, 0
    if len(hist) == hist.maxlen:
        dx = hist[-1][0] - hist[0][0]
        dy = hist[-1][1] - hist[0][1]
        dz = hist[-1][2] - hist[0][2]
        dt = 0.05 * (len(hist) - 1)
        vx = dx / dt
        vz = dz / dt

        # --- Swipe detection (any hand shape, facing camera) ---
        if abs(vx) > 400 and vz > -0.004:  # detect faster sideways motion
            direction = "RIGHT" if vx > 0 else "LEFT"
            if mirror_flip:
                direction = "LEFT" if direction == "RIGHT" else "RIGHT"

            now = time.time()
            last = state[label]["last_swipe"]
            if last["dir"] != direction or (now - last["time"] > 0.8):
                gesture += f"_SWIPE_{direction}"
                state[label]["last_swipe"] = {
                    "text": f"{label} SWIPED {direction.upper()}!",
                    "time": now,
                    "dir": direction
                }
                send_midi_note(label, note=64 if direction == "RIGHT" else 65)

        # --- Vertical movement (volume control) ---
        elif abs(dy) > 30 and abs(dy) > abs(dx):
            vol = state[label]["volume"]
            vol += -dy * 0.1
            prev_vol = state[label]["prev_volume"]
            smoothed = 0.7 * prev_vol + 0.3 * vol
            state[label]["prev_volume"] = smoothed
            state[label]["volume"] = np.clip(smoothed, 0, 100)
            send_midi_cc(label, 7, int(state[label]["volume"]))

    # Static gestures
    if gesture == "FIST":
        send_midi_note(label, 60)
    elif gesture == "OPEN_PALM":
        send_midi_note(label, 62)
    elif gesture == "SHAKA":
        send_midi_note(label, 66)
    elif gesture == "PEACE":
        send_midi_cc(label, 91, 127)

    return gesture, up_count, state[label]["volume"]


def detect(frame):
    """Detect hands, classify gestures, draw overlay, and return structured results."""
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    if not result.multi_hand_landmarks:
        return []

    h, w, _ = frame.shape
    outputs = []
    for i, handLms in enumerate(result.multi_hand_landmarks):
        label = result.multi_handedness[i].classification[0].label
        pts = np.array([[lm.x * w, lm.y * h, lm.z] for lm in handLms.landmark])
        gesture, count, volume = classify_hand_state(label, pts)
        outputs.append({
            "hand": label,
            "gesture": gesture,
            "fingers": count,
            "volume": int(volume),
            "ts": time.time()
        })
        mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
    return outputs


# ------------------------------------------------------------
# Run directly for debugging
# ------------------------------------------------------------
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("AirDJ — universal swipe detection active")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        results = detect(frame)
        h, w, _ = frame.shape

        left_x = 150
        right_x = w // 2 + 200
        y_base = 150

        for r in results:
            hand = r["hand"]
            x_pos = left_x if hand == "Left" else right_x
            y = y_base

            overlay = frame.copy()
            cv2.rectangle(overlay, (x_pos - 20, y - 40),
                          (x_pos + 450, y + 130), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

            cv2.putText(frame, f"{hand}: {r['gesture']}", (x_pos, y),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)
            cv2.putText(frame, f"Fingers: {r['fingers']} | Vol: {r['volume']}",
                        (x_pos, y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            # Volume bar
            bar_x = x_pos
            bar_y = h - 150
            vol_height = int((r['volume'] / 100) * 300)
            cv2.rectangle(frame, (bar_x, bar_y - vol_height),
                          (bar_x + 60, bar_y), (0, 255, 0), -1)
            cv2.rectangle(frame, (bar_x, bar_y - 300),
                          (bar_x + 60, bar_y), (255, 255, 255), 3)

            wave_info = state[hand]["last_swipe"]
            if time.time() - wave_info["time"] < 1.5:
                cv2.putText(frame, wave_info["text"],
                            (x_pos, bar_y - 350),
                            cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 255), 3)

        cv2.imshow("AirDJ — Any-Hand Swipe Tracker", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in [27, ord('x'), ord('X')]:
            break

    cap.release()
    cv2.destroyAllWindows()
