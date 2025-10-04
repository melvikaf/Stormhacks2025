import cv2, time, numpy as np
import mediapipe as mp
from collections import deque

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.6)

left_wrist_hist = deque(maxlen=5)
right_wrist_hist = deque(maxlen=5)

def classify_pose_and_motion(label, pts):
    wrist = pts[0]
    fingertips = pts[[4,8,12,16,20]]
    mids = pts[[3,6,10,14,18]]
    folded_ratio = np.mean(fingertips[:,1] > mids[:,1])
    gesture = None
    conf = 0.9

    # static
    if folded_ratio > 0.8:
        gesture = "FIST"
    elif folded_ratio < 0.2:
        gesture = "OPEN_PALM"
    else:
        if (pts[4][0] < pts[3][0] and pts[20][1] < pts[18][1] and
            pts[8][1] > pts[6][1] and pts[12][1] > pts[10][1] and pts[16][1] > pts[14][1]):
            gesture = "SHAKA"
        else:
            gesture = "UNKNOWN"

    # motion
    hist = left_wrist_hist if label == "Left" else right_wrist_hist
    hist.append(wrist)
    if len(hist) == hist.maxlen:
        dx = hist[-1][0] - hist[0][0]
        dy = hist[-1][1] - hist[0][1]
        if abs(dx) > 50 and abs(dx) > abs(dy):
            gesture = "WAVE_RIGHT" if dx > 0 else "WAVE_LEFT"
        elif abs(dy) > 50:
            gesture = "WAVE_DOWN" if dy > 0 else "WAVE_UP"

    return gesture, conf


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
        gesture, conf = classify_pose_and_motion(label, pts)
        outputs.append({"hand": label, "gesture": gesture, "conf": conf, "ts": time.time()})
        mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
    return outputs


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        results = detect(frame)
        y = 60
        for r in results:
            cv2.putText(frame, f"{r['hand']}: {r['gesture']}", (30, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,255), 3)
            y += 50
        cv2.imshow("AirDJ Gestures", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
