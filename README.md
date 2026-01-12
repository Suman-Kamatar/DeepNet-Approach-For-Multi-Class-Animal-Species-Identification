# Wild Animal Alert System 🐾🚀

A real-time AI-powered monitoring system designed to detect wild animals using YOLO-World and trigger multi-channel alerts (Sound, Email, and SMS) when dangerous animals are identified.

## 🌟 Key Features

- **Real-time Detection**: Uses YOLO-World (v8s-worldv2) for open-vocabulary object detection.
- **Intelligent Classification**: Categorizes detections into three tiers:
    - 🟢 **Domestic & Safe**: Cats, Dogs, Cattle, etc.
    - 🟡 **Wild & Safe**: Deer, Monkeys, Rabbits, etc.
    - 🔴 **Wild & Dangerous**: Lions, Tigers, Bears, etc. (Triggers immediate alerts).
- **Multi-Channel Alerts**:
    - 🔊 **Audio**: High-decibel alert sound played locally.
    - 📧 **Email**: Instant photographic notification via SMTP.
    - 📱 **SMS**: Text alerts via Twilio (Configuration required).
- **Web Interface**: A clean, responsive dashboard for live camera feeds and static image testing.
- **Optimized Performance**: Frame skipping and inference resizing for smooth real-time operation on standard hardware.

## 🛠️ Project Structure

- `app.py`: The core Flask application handling the web server, socket connections, and detection logic.
- `alert_system.py`: Manages the alert logic, including sound playback and notification dispatching.
- `config.py`: Centralized configuration for animal categories, confidence thresholds, and notification credentials.
- `main.py`: Entry point for launching the detection engine.
- `train.py`: Script for training or fine-tuning the YOLO model.
- `auto_label.py`: Automated dataset labeling tool.
- `templates/` & `static/`: Frontend assets for the web dashboard.

## 🚀 Quick Start

### 1. Requirements
- Python 3.8+
- OpenCV
- Ultralytics (YOLOv8)
- Flask & Flask-SocketIO
- Pygame (for audio alerts)

### 2. Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your credentials in `config.py` (Email, Twilio, etc.).

### 3. Run
Launch the application:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:8080`.

## ⚙️ Configuration

Edit `config.py` to customize:
- **Animals**: Add or remove animals from the SAFE/DANGEROUS lists.
- **Thresholds**: Adjust `CONFIDENCE_THRESHOLD` for detection sensitivity.
- **Alerts**: Set `NOTIFICATION_METHOD` to 'EMAIL', 'SMS', or 'BOTH'.

---
*Developed as a project for wild animal conservation and human safety.*
