import cv2
import os
from ultralytics import YOLO
import config
from alert_system import AlertSystem

def main():
    # 1. Initialize Alert System
    alert_system = AlertSystem()

    # 2. Load Model
    # 2. Load Model
    # Try custom model first for high accuracy on 10 core classes
    custom_model_path = os.path.join("runs", "detect", "my_animal_model2", "weights", "best.pt")
    
    if os.path.exists(custom_model_path):
        print(f"[INFO] Loading Custom Trained Model ({custom_model_path})...")
        try:
            model = YOLO(custom_model_path)
            model_type = "CUSTOM"
        except Exception as e:
            print(f"[WARN] Failed to load custom model: {e}. Falling back to YOLO-World.")
            model = None
    else:
        model = None

    # Fallback to YOLO-World for open vocabulary
    if model is None:
        print(f"[INFO] Loading YOLO-World model (yolov8s-worldv2.pt)...")
        try:
            model = YOLO("yolov8s-worldv2.pt")
            model.set_classes(config.ANIMAL_VOCABULARY)
            model_type = "WORLD"
            print(f"[INFO] YOLO-World Vocabulary set.")
        except Exception as e:
            print(f"[ERROR] Failed to load YOLO-World: {e}")
            return 

    # 3. Initialize Video Capture
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open video device.")
        return

    print(f"[INFO] Started detection. Press 'q' to quit.")

    count = 0
    last_detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        count += 1
        h, w = frame.shape[:2]
        
        # Scale for coordinate mapping
        scale_factor = w / config.DETECTION_WIDTH

        # 4. Inferences (Only on every Nth frame)
        if count % config.FRAME_SKIP == 1:
            # Resize for speed
            small_frame = cv2.resize(frame, (config.DETECTION_WIDTH, int(h / scale_factor)))
            
            # Predict
            results = model(small_frame, stream=False, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
            
            current_detections = []
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    label_name = model.names[cls_id]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Mapping and filtering
                    display_name = label_name
                    category = None
                    
                    if label_name in config.WILD_DANGEROUS_ANIMALS:
                        category = "DANGER"
                        display_name = config.WILD_DANGEROUS_ANIMALS[label_name]
                    elif label_name in config.WILD_SAFE_ANIMALS:
                        category = "WILD(Safe)"
                        display_name = config.WILD_SAFE_ANIMALS[label_name]
                    elif label_name in config.DOMESTIC_SAFE_ANIMALS:
                        category = "DOMESTIC"
                        display_name = config.DOMESTIC_SAFE_ANIMALS[label_name]
                    
                    # Thresholds
                    min_conf = config.DANGER_CONFIDENCE_MIN if category == "DANGER" else config.SAFE_CONFIDENCE_MIN
                    if conf < min_conf: continue

                    current_detections.append({
                        'name': display_name,
                        'cat': category,
                        'conf': conf,
                        'box': [x1, y1, x2, y2]
                    })
                    
                    if category == "DANGER":
                        alert_system.trigger_alert(display_name)
            
            last_detections = current_detections

        # 5. Draw latest detections on current frame
        for det in last_detections:
            x1, y1, x2, y2 = det['box']
            # Scale back up
            x1, y1 = int(x1 * scale_factor), int(y1 * scale_factor)
            x2, y2 = int(x2 * scale_factor), int(y2 * scale_factor)
            
            category = det['cat']
            display_name = det['name']
            conf = det['conf']

            color = (255, 255, 255) # White default
            if category == "DANGER": color = (0, 0, 255)
            elif category == "WILD(Safe)": color = (0, 255, 255)
            elif category == "DOMESTIC": color = (0, 255, 0)

            label_text = f"{category}: {display_name} {conf:.2f}" if category else f"{display_name} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label_text, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 6. Show Frame
        cv2.imshow("Wild Animal Detection System", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
