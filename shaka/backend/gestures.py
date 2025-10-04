import cv2, time, numpy as np
import mediapipe as mp
from collections import deque

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

left_hist = deque(maxlen=5)
right_hist = deque(maxlen=5)

state = {
    "Left": {"volume": 50, "last_wave": {"text": "", "time": 0}},
    "Right": {"volume": 50, "last_wave": {"text": "", "time": 0}},
}

# ---------- Helper Functions ----------
def get_finger_states(pts, label):
    states = {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0}

    # Thumb (horizontal check)
    if label == "Right":
        states["thumb"] = int(pts[4][0] > pts[3][0])
    else:
        states["thumb"] = int(pts[4][0] < pts[3][0])

    # Other fingers (vertical check)
    for name, tip, mid in zip(["index", "middle", "ring", "pinky"],
                              [8, 12, 16, 20], [6, 10, 14, 18]):
        states[name] = int(pts[tip][1] < pts[mid][1])
    return states


def classify_hand_state(label, pts):
    wrist = pts[0]
    fingers = get_finger_states(pts, label)
    up_count = sum(fingers.values())
    gesture = "UNKNOWN"

    # Base gestures
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

    # Motion detection
    hist = left_hist if label == "Left" else right_hist
    hist.append(wrist)
    if len(hist) == hist.maxlen:
        dx = hist[-1][0] - hist[0][0]
        dy = hist[-1][1] - hist[0][1]

        # Horizontal wave
        if abs(dx) > 60 and abs(dx) > abs(dy):
            direction = "RIGHT" if dx > 0 else "LEFT"
            gesture += f"_WAVE_{direction}"
            state[label]["last_wave"]["text"] = f"{label} WAVED {direction.upper()}!"
            state[label]["last_wave"]["time"] = time.time()

        # Vertical motion → volume
        elif abs(dy) > 60 and abs(dy) > abs(dx):
            vol = state[label]["volume"]
            vol += -dy * 0.4
            state[label]["volume"] = np.clip(vol, 0, 100)

    return gesture, up_count, state[label]["volume"]


def detect(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    if not result.multi_hand_landmarks:
        return []

    h, w, _ = frame.shape
    outputs = []
    for i, handLms in enumerate(result.multi_hand_landmarks):
        label = result.multi_handedness[i].classification[0].label
        pts = np.array([[lm.x * w, lm.y * h] for lm in handLms.landmark])
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


# ---------- Main ----------
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)

        results = detect(frame)
        h, w, _ = frame.shape

        # Two distinct UI regions
        left_x = 150
        right_x = w // 2 + 200
        y_base = 150

        for r in results:
            hand = r["hand"]
            x_pos = left_x if hand == "Left" else right_x
            y = y_base

            # Draw translucent background rectangle
            overlay = frame.copy()
            cv2.rectangle(overlay, (x_pos - 20, y - 40), (x_pos + 450, y + 130),
                          (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

            # Text
            text = f"{hand}: {r['gesture']}"
            cv2.putText(frame, text, (x_pos, y),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)
            cv2.putText(frame, f"Fingers: {r['fingers']} | Vol: {r['volume']}",
                        (x_pos, y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            # Volume bar (taller + lower position)
            bar_x = x_pos
            bar_y = h - 150
            vol_height = int((r['volume'] / 100) * 300)
            cv2.rectangle(frame, (bar_x, bar_y - vol_height),
                          (bar_x + 60, bar_y), (0, 255, 0), -1)
            cv2.rectangle(frame, (bar_x, bar_y - 300),
                          (bar_x + 60, bar_y), (255, 255, 255), 3)

            # Wave notification (per hand)
            wave_info = state[hand]["last_wave"]
            if time.time() - wave_info["time"] < 1.5:
                cv2.putText(frame, wave_info["text"],
                            (x_pos, bar_y - 350),
                            cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 255), 3)

        cv2.imshow("🎧 AirDJ — Full HD Dual-Hand Tracker", frame)
        key = cv2.waitKey(1) & 0xFF
        # Press 'Esc' OR 'X' to close
        if key == 27 or key == ord('x') or key == ord('X'):
            break

    cap.release()
    cv2.destroyAllWindows()
