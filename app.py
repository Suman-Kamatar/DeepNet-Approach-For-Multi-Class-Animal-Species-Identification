import cv2
import os
import time
import base64
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
import config
from alert_system import AlertSystem

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
alert_system = AlertSystem()

# Global states
model = None
model_type = "NONE"

def load_system_model():
    global model, model_type
    print("[INFO] Initializing Detection Engine...")
    
    # Force YOLO-World for reliability with current vocabulary
    try:
        model = YOLO("yolov8s-worldv2.pt")
        model.set_classes(config.ANIMAL_VOCABULARY)
        model_type = "WORLD"
        print("[SUCCESS] YOLO-World loaded (Person detection priority).")
    except Exception as e:
        print(f"[ERROR] Failed to load YOLO-World: {e}. Falling back to Nano.")
        model = YOLO("yolov8n.pt")
        model_type = "NANO"

def process_frame(frame, send_alert=True):
    """Detects animals in a frame without drawing on it."""
    if model is None: return []
    
    results = model.predict(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
    detections = []
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label_name = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Class mapping and filtering (simplified version of the previous logic)
            display_name = label_name
            category = "DOMESTIC"
            
            if "person" in label_name or "human" in label_name:
                display_name = "person"
            elif label_name in config.WILD_DANGEROUS_ANIMALS:
                category = "DANGER"
                display_name = config.WILD_DANGEROUS_ANIMALS[label_name]
            elif label_name in config.WILD_SAFE_ANIMALS:
                category = "WILD"
                display_name = config.WILD_SAFE_ANIMALS[label_name]
            elif label_name in config.DOMESTIC_SAFE_ANIMALS:
                display_name = config.DOMESTIC_SAFE_ANIMALS[label_name]

            min_conf = config.DANGER_CONFIDENCE_MIN if category == "DANGER" else config.SAFE_CONFIDENCE_MIN
            if conf < min_conf: continue

            detections.append({
                'name': display_name,
                'type': category.lower(),
                'conf': round(conf, 2),
                'box': [x1, y1, x2, y2]
            })

            if send_alert and category == "DANGER":
                alert_system.trigger_alert(display_name)
                
    return detections

def draw_detections(frame, detections, scale_factor=1.0):
    """Draws bounding boxes and labels on the frame."""
    for det in detections:
        x1, y1, x2, y2 = det['box']
        
        # Scale coordinates if inference was done on a smaller frame
        x1, y1 = int(x1 * scale_factor), int(y1 * scale_factor)
        x2, y2 = int(x2 * scale_factor), int(y2 * scale_factor)
        
        category = det['type'].upper()
        display_name = det['name']
        
        color = (0, 0, 255) if category == "DANGER" else (0, 255, 0)
        if category == "WILD": color = (0, 255, 255)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{category}: {display_name}", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame

def generate_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): return

    count = 0
    last_detections = []
    
    while True:
        success, frame = cap.read()
        if not success: break
        
        count += 1
        h, w = frame.shape[:2]
        
        # Determine scale factor for inference
        scale_factor = w / config.DETECTION_WIDTH
        
        # Only process every Nth frame for performance
        if count % config.FRAME_SKIP == 1:
            # Resize frame for FASTER inference
            small_frame = cv2.resize(frame, (config.DETECTION_WIDTH, int(h / scale_factor)))
            
            # Predict on small frame (returns list of detection objects)
            last_detections = process_frame(small_frame, send_alert=True)
            
            # Emit detections to socket
            for d in last_detections:
                socketio.emit('detection', {k: v for k, v in d.items() if k != 'box'})

        # Draw detections (scaled back up) on the high-res frame
        annotated_frame = draw_detections(frame.copy(), last_detections, scale_factor=scale_factor)

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret: continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', model_type=model_type)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    return jsonify({'status': 'stopped'})

@app.route('/detect_static', methods=['POST'])
def detect_static():
    if 'image' not in request.files: return jsonify({'error': 'No image'}), 400
    
    file = request.files['image']
    nparr = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Process with alerts enabled
    detections = process_frame(frame, send_alert=True)
    
    # Draw detections for response image
    annotated_frame = draw_detections(frame.copy(), detections)
    
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    encoded_img = base64.b64encode(buffer).decode('utf-8')
    
    # Remove boxes from json response for clean data
    clean_detections = [{k: v for k, v in d.items() if k != 'box'} for d in detections]
    
    return jsonify({
        'detections': clean_detections,
        'image': f"data:image/jpeg;base64,{encoded_img}"
    })

if __name__ == '__main__':
    load_system_model()
    socketio.run(app, debug=True, host='127.0.0.1', port=8080)
