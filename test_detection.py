import cv2
import os
from ultralytics import YOLO
import config
from alert_system import AlertSystem

def test_detection(image_path):
    print(f"\n[TEST] Testing image: {image_path}")
    
    # 1. Initialize Alert System
    alert_system = AlertSystem()

    # 2. Load YOLO-World Model
    try:
        model = YOLO("yolov8s-worldv2.pt")
        model.set_classes(config.ANIMAL_VOCABULARY)
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return

    # 3. Read Image
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"[ERROR] Could not read image: {image_path}")
        return

    # 4. Inference
    results = model(frame, conf=config.CONFIDENCE_THRESHOLD)

    for result in results:
        boxes = result.boxes
        if not boxes:
            print("  > No animals detected.")
        
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label_name = model.names[cls_id]

            # Category determination based on new descriptive labels
            category = "UNKNOWN"
            display_name = label_name
            if label_name in config.WILD_DANGEROUS_ANIMALS:
                category = "DANGER"
                display_name = config.WILD_DANGEROUS_ANIMALS[label_name]
                alert_system.trigger_alert(display_name)
            elif label_name in config.WILD_SAFE_ANIMALS:
                category = "WILD(Safe)"
                display_name = config.WILD_SAFE_ANIMALS[label_name]
            elif label_name in config.DOMESTIC_SAFE_ANIMALS:
                category = "DOMESTIC"
                display_name = config.DOMESTIC_SAFE_ANIMALS[label_name]

            print(f"  > Detected: {display_name} ({category}) - Confidence: {conf:.2f}")

if __name__ == "__main__":
    # Test with a few sample images from the project folders if they exist
    test_folders = ["animals/tiger", "animals/cat", "animals/lion", "animals/fox"]
    
    for folder in test_folders:
        full_path = os.path.join(os.getcwd(), folder)
        if os.path.exists(full_path):
            images = [f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                test_detection(os.path.join(full_path, images[0]))
            else:
                print(f"[WARN] No images found in {folder}")
        else:
            print(f"[WARN] Folder not found: {folder}")
