# Move With Traffic - Smart Traffic Control System

A computer-vision based traffic signal demo that analyzes a traffic video stream in real time and changes signal status based on road density.

Live Demo (Backend on Render): https://move-with-traffic.onrender.com

Frontend Demo on GitHub Pages: https://prudviraj12345.github.io/Move-With-Traffic/

Repository: https://github.com/prudviraj12345/Move-With-Traffic

## Project Overview

This project simulates an intelligent traffic signal controller using video processing.

The system reads a traffic video, extracts edges using Canny Edge Detection, estimates traffic density from edge pixels, detects vehicle-like contours, and updates signal state dynamically.

The dashboard shows:
- Original traffic feed
- Edge detection feed
- Live metrics (density, vehicles, level)
- Signal color and timer

## Why This Project

Traditional fixed-timer signals do not react to real road conditions.

This project demonstrates a simple adaptive model where signal decisions are made from observed traffic density, which can reduce unnecessary waiting on low-traffic roads and prioritize busy lanes.

## How We Built It

1. Video Processing Layer
- Reads frames from traffic.mp4 using OpenCV
- Resizes frame for consistent processing
- Converts to grayscale and applies Gaussian blur
- Runs Canny edge detection
- Computes density from non-zero edge pixels
- Finds contours and filters them to estimate vehicle count

2. Signal Decision Layer
- LOW density -> RED SIGNAL
- MEDIUM density -> YELLOW SIGNAL
- HIGH density -> GREEN SIGNAL
- Tracks signal active duration in seconds

3. Web Streaming + API Layer
- Flask serves the dashboard
- MJPEG endpoints stream original and edge frames
- Status endpoint returns live JSON metrics

4. Frontend Layer
- HTML/CSS dashboard with traffic-light visualization
- JavaScript polls status endpoint and updates values every 500 ms

## Tech Stack

- Python
- Flask
- OpenCV
- NumPy
- Gunicorn (production server on Render)
- HTML
- CSS
- JavaScript
- Render (backend hosting)
- GitHub Pages (static frontend demo)

## Project Structure

- app.py: Main Flask application, processing thread, routes, API, stream endpoints
- traffic.py: Standalone local script for quick OpenCV edge demo
- traffic.mp4: Input traffic video
- templates/index.html: Flask-rendered dashboard page
- static/style.css: Dashboard styles
- index.html: Static frontend-only page for GitHub Pages
- requirements.txt: Python dependencies
- render.yaml: Render service blueprint
- runtime.txt: Python runtime version for cloud deployment
- pyrightconfig.json: Python type-check settings

## System Workflow

1. App starts and creates background processor thread.
2. Frames are continuously read and analyzed.
3. Density and vehicle count are calculated.
4. Signal state is selected based on thresholds.
5. Processed frames are encoded as JPEG and cached.
6. Browser receives streams and metric updates in real time.

## API and Routes

- GET / : Dashboard page
- GET /video_feed/original : Original MJPEG stream
- GET /video_feed/edges : Edge MJPEG stream
- GET /status : JSON with density, vehicle_count, traffic_level, signal, signal_timer_seconds, error

## Local Setup and Run

### Prerequisites

- Python 3.10+ (3.11 recommended)
- Git

### 1) Clone the repository

    git clone https://github.com/prudviraj12345/Move-With-Traffic.git
    cd Move-With-Traffic

### 2) Create virtual environment

Windows PowerShell:

    python -m venv .venv

macOS/Linux:

    python3 -m venv .venv

### 3) Activate virtual environment

Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

Windows CMD:

    .venv\Scripts\activate.bat

macOS/Linux:

    source .venv/bin/activate

### 4) Install dependencies

    pip install -r requirements.txt

### 5) Run the Flask app

    python app.py

### 6) Open in browser

    http://127.0.0.1:5000

## Render Deployment

This repository is already configured for Render using render.yaml.

### Option A: One-click deploy

https://render.com/deploy?repo=https://github.com/prudviraj12345/Move-With-Traffic

### Option B: Manual deploy

1. Create a new Web Service on Render.
2. Connect this GitHub repository.
3. Render reads render.yaml automatically.
4. Deploy and wait for build completion.

Expected live URL:
https://move-with-traffic.onrender.com

## GitHub Pages Deployment (Frontend Only)

GitHub Pages can host only static content, so this is a frontend demo mode.

Live static URL:
https://prudviraj12345.github.io/Move-With-Traffic/

## Key Implementation Notes

- OpenCV runs in a background thread to keep stream generation responsive.
- Shared frame and metrics data are guarded with a thread lock.
- The app loops the video when it reaches the end for continuous demo behavior.
- On video load failure, fallback error frames are generated and returned.

## Future Improvements

- Replace heuristic contour filtering with trained object detection
- Add lane-wise density estimation
- Add historical charts and analytics
- Add config page for threshold tuning
- Add unit and integration tests

## Author

Prudviraj

## License

Add a license file if you want open-source reuse (for example MIT).
