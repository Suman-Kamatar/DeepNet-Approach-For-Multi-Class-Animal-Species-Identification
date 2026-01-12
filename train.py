from ultralytics import YOLO

def train_model():
    # 1. Load a model
    # yolov8n.pt is the Nano model (smallest/fastest). good for real-time.
    # You can also use yolov8s.pt, yolov8m.pt, etc. for better accuracy but slower speed.
    model = YOLO("yolov8n.pt") 

    # 2. Train the model
    # 'data' argument should point to your data.yaml file
    # 'epochs' is how many times to go through the dataset
    results = model.train(
        data="data.yaml",  # Path to your dataset config
        epochs=50,         # Start with 50 epochs
        imgsz=640,         # Image size
        batch=16,          # Batch size
        name="my_animal_model" # Project name for saving results
    )

    # 3. Validation
    metrics = model.val() # Evaluate model performance on the validation set
    print(metrics.box.map) # map50-95

    # 4. Export
    success = model.export(format="onnx")  # Export the model to ONNX format (optional)

if __name__ == "__main__":
    print("Starting Training Process...")
    print("Ensure you have your dataset ready and 'data.yaml' configured correctly.")
    train_model()
