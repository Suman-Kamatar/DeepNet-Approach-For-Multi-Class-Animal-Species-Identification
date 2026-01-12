import os
import shutil
import random
from ultralytics import YOLO
import glob

# --- Configuration ---
SOURCE_DIRS = ["dataset/dataset", "animals"] 
DATA_DIR = "data"
TRAIN_RATIO = 0.8

# Map Class IDs to potential folder names (Scientific & Common)
CLASS_MAPPING = {
    0: ["cat", "felis-catus"],
    1: ["dog", "canis-lupus-familiaris"],
    2: ["horse", "equus-caballus"],
    3: ["cow", "bos-taurus"],
    4: ["tiger", "panthera-tigris"],
    5: ["fox", "vulpes-vulpes"],
    6: ["lion", "panthera-leo"],
    7: ["cheetah", "cheeta", "acinonyx-jubatus"],
    8: ["hyena"],
    9: ["wolf", "canis-lupus"],
    10: ["person", "human", "homo-sapiens"]
}

def auto_label_dataset():
    # 1. Setup Directories
    for split in ['train', 'val']:
        for dtype in ['images', 'labels']:
            os.makedirs(os.path.join(DATA_DIR, split, dtype), exist_ok=True)

    # 2. Load YOLO-World Model
    print("Loading YOLO-World model for auto-labeling...")
    try:
        model = YOLO('yolov8s-worldv2.pt')
        # Use a global vocabulary for ALL images to prevent "forced" misclassification
        vocabulary = [CLASS_MAPPING[i][0] for i in range(len(CLASS_MAPPING))]
        model.set_classes(vocabulary)
        print(f"Global vocabulary set: {vocabulary}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Create mapping from detected names back to IDs
    name_to_id = {CLASS_MAPPING[i][0]: i for i in range(len(CLASS_MAPPING))}

    # 3. Collect All Images
    all_images = []
    for source_root in SOURCE_DIRS:
        if os.path.exists(source_root):
            all_images.extend(glob.glob(os.path.join(source_root, "**", "*.*"), recursive=True))
    
    # Filter for valid image extensions
    valid_images = [img for img in all_images if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    print(f"Found {len(valid_images)} total images to process.")

    random.shuffle(valid_images)
    split_idx = int(len(valid_images) * TRAIN_RATIO)
    
    train_imgs = valid_images[:split_idx]
    val_imgs = valid_images[split_idx:]
    
    process_batch(model, train_imgs, 'train', name_to_id)
    process_batch(model, val_imgs, 'val', name_to_id)

def process_batch(model, image_paths, split, name_to_id):
    total = len(image_paths)
    print(f"    -> Starting {split} split ({total} images)...")
    
    for i, img_path in enumerate(image_paths):
        if i % 50 == 0:
            print(f"       Processing {i}/{total}...")
            
        filename = os.path.basename(img_path)
        # Handle duplicate filenames
        stem = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        
        target_img_dir = os.path.join(DATA_DIR, split, 'images')
        target_label_dir = os.path.join(DATA_DIR, split, 'labels')
        
        final_filename = filename
        if os.path.exists(os.path.join(target_img_dir, final_filename)):
            final_filename = f"{random.randint(1000,9999)}_{filename}"
            stem = os.path.splitext(final_filename)[0]

        dest_img_path = os.path.join(target_img_dir, final_filename)
        dest_label_path = os.path.join(target_label_dir, stem + ".txt")
        
        try:
            # 1. Determine Ground Truth Class from Folder Name
            parent_dir = os.path.basename(os.path.dirname(img_path)).lower()
            gt_class_id = None
            
            # Check if parent folder matches any of our classes
            for cid, names in CLASS_MAPPING.items():
                if any(n in parent_dir for n in names):
                    gt_class_id = cid
                    break

            # 2. Run Inference to get Bounding Boxes
            results = model.predict(img_path, conf=0.15, verbose=False, save=False)
            
            if results[0].boxes:
                shutil.copy2(img_path, dest_img_path)
                with open(dest_label_path, "w") as f:
                    for box in results[0].boxes:
                        # Use Ground Truth if found, otherwise fallback to model's best guess
                        if gt_class_id is not None:
                            class_id = gt_class_id
                        else:
                            cls_name = model.names[int(box.cls[0])]
                            class_id = name_to_id.get(cls_name, -1)
                        
                        if class_id != -1:
                            x, y, w, h = box.xywhn[0].tolist()
                            f.write(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue

if __name__ == "__main__":
    auto_label_dataset()
    print("\n[DONE] Dataset re-prepared with 'person' class and global accuracy settings.")
