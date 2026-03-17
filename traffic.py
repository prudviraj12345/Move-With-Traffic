from pathlib import Path

import cv2

project_dir = Path(__file__).resolve().parent
video_path = project_dir / "traffic.mp4"

if not video_path.exists():
    print(f"Error: Video file not found at: {video_path}")
    print("Place traffic.mp4 in the same folder as traffic.py and run again.")
    raise SystemExit(1)

cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    print(f"Error: Could not open video file: {video_path}")
    print("Check that the file is a valid playable video and not locked by another app.")
    raise SystemExit(1)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blur, 50, 150)

    density = cv2.countNonZero(edges)

    if density > 20000:
        signal = "GREEN SIGNAL"
    elif density > 10000:
        signal = "YELLOW SIGNAL"
    else:
        signal = "RED SIGNAL"

    cv2.putText(frame, f"Density: {density}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.putText(frame, f"Signal: {signal}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Traffic Feed", frame)
    cv2.imshow("Edge Detection", edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()