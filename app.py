import threading
import time
import os
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template

app = Flask(__name__)


class TrafficProcessor:
    def __init__(self, video_filename: str = "traffic.mp4", target_fps: int = 9):
        self.video_path = Path(__file__).resolve().parent / video_filename
        self.target_fps = target_fps
        self.frame_delay = 1.0 / float(target_fps)

        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        self.original_jpeg = None
        self.edge_jpeg = None
        self.density = 0
        self.vehicle_count = 0
        self.traffic_level = "LOW"
        self.signal = "RED SIGNAL"
        self.signal_changed_at = time.time()
        self.signal_timer_seconds = 0
        self.error_message = ""

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _set_error_frame(self, message: str):
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "SMART TRAFFIC CONTROL SYSTEM", (25, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
        cv2.putText(error_frame, "Video Error:", (25, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.putText(error_frame, message[:58], (25, 280),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ok1, original_buf = cv2.imencode('.jpg', error_frame)
        gray = cv2.cvtColor(error_frame, cv2.COLOR_BGR2GRAY)
        ok2, edge_buf = cv2.imencode('.jpg', gray)

        if ok1 and ok2:
            with self.lock:
                self.original_jpeg = original_buf.tobytes()
                self.edge_jpeg = edge_buf.tobytes()
                self.density = 0
                self.vehicle_count = 0
                self.traffic_level = "LOW"
                self.signal = "RED SIGNAL"
                self.signal_changed_at = time.time()
                self.signal_timer_seconds = 0
                self.error_message = message

    def _process_loop(self):
        if not self.video_path.exists():
            msg = f"Video file not found: {self.video_path}"
            print(f"[ERROR] {msg}")
            self._set_error_frame(msg)
            return

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            msg = f"Could not open video: {self.video_path}"
            print(f"[ERROR] {msg}")
            self._set_error_frame(msg)
            return

        while self.running:
            start_time = time.time()
            ret, frame = cap.read()

            # Loop the video to keep the demo running continuously.
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blur, 50, 150)
            edge_for_contours = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

            density = int(cv2.countNonZero(edges))

            if density < 10000:
                traffic_level = "LOW"
            elif density < 20000:
                traffic_level = "MEDIUM"
            else:
                traffic_level = "HIGH"

            contours, _ = cv2.findContours(edge_for_contours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            vehicle_boxes = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 120:
                    continue

                x, y, w, h = cv2.boundingRect(contour)
                if w < 15 or h < 12:
                    continue

                aspect_ratio = w / float(h)
                if aspect_ratio < 0.2 or aspect_ratio > 6.0:
                    continue

                vehicle_boxes.append((x, y, w, h))

            vehicle_count = len(vehicle_boxes)

            if density > 20000:
                signal = "GREEN SIGNAL"
                color = (0, 220, 0)
            elif density > 10000:
                signal = "YELLOW SIGNAL"
                color = (0, 255, 255)
            else:
                signal = "RED SIGNAL"
                color = (0, 0, 255)

            if signal != self.signal:
                self.signal_changed_at = time.time()

            signal_timer_seconds = int(time.time() - self.signal_changed_at)

            for x, y, w, h in vehicle_boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 170, 0), 2)

            cv2.putText(frame, f"Traffic Density: {density}", (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.putText(frame, f"Signal Status: {signal}", (15, 68),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
            cv2.putText(frame, f"Traffic Level: {traffic_level}", (15, 101),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
            cv2.putText(frame, f"Vehicles Detected: {vehicle_count}", (15, 134),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
            cv2.putText(frame, f"Signal Time: {signal_timer_seconds} sec", (15, 167),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, color, 2)

            edge_view = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            cv2.putText(edge_view, f"Edge Pixels: {density}", (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.putText(edge_view, f"Signal: {signal}", (15, 68),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
            cv2.putText(edge_view, f"Traffic Level: {traffic_level}", (15, 101),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
            cv2.putText(edge_view, f"Vehicles: {vehicle_count}", (15, 134),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
            cv2.putText(edge_view, f"Signal Time: {signal_timer_seconds} sec", (15, 167),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, color, 2)

            for x, y, w, h in vehicle_boxes:
                cv2.rectangle(edge_view, (x, y), (x + w, y + h), (255, 170, 0), 2)

            ok1, original_buf = cv2.imencode('.jpg', frame)
            ok2, edge_buf = cv2.imencode('.jpg', edge_view)

            if ok1 and ok2:
                with self.lock:
                    self.original_jpeg = original_buf.tobytes()
                    self.edge_jpeg = edge_buf.tobytes()
                    self.density = density
                    self.vehicle_count = vehicle_count
                    self.traffic_level = traffic_level
                    self.signal = signal
                    self.signal_timer_seconds = signal_timer_seconds
                    self.error_message = ""

            elapsed = time.time() - start_time
            if elapsed < self.frame_delay:
                time.sleep(self.frame_delay - elapsed)

        cap.release()


processor = TrafficProcessor(video_filename="traffic.mp4", target_fps=9)


def _stream_generator(stream_name: str):
    while True:
        with processor.lock:
            frame = processor.original_jpeg if stream_name == "original" else processor.edge_jpeg

        if frame is None:
            time.sleep(0.05)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/")
def index():
    processor.start()
    return render_template("index.html")


@app.route("/video_feed/original")
def video_feed_original():
    processor.start()
    return Response(
        _stream_generator("original"),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/video_feed/edges")
def video_feed_edges():
    processor.start()
    return Response(
        _stream_generator("edges"),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/status")
def status():
    with processor.lock:
        payload = {
            "density": processor.density,
            "vehicle_count": processor.vehicle_count,
            "traffic_level": processor.traffic_level,
            "signal": processor.signal,
            "signal_timer_seconds": processor.signal_timer_seconds,
            "error": processor.error_message,
        }
    return jsonify(payload)


if __name__ == "__main__":
    processor.start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
