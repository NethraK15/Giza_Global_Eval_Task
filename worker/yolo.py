from ultralytics import YOLO
import os

class YoloModel:
    def __init__(self, model_path="yolov8n.pt"):
        print(f"Loading YOLO model from {model_path}...")
        # Use the models directory if available
        if os.path.exists("/models"):
            model_file = os.path.join("/models", model_path)
            if os.path.exists(model_file):
                print(f"Using model from mounted volume: {model_file}")
                self.model = YOLO(model_file)
            else:
                print(f"Model file {model_file} not found in /models. falling back to {model_path} (will download if standard model)")
                self.model = YOLO(model_path)
        else:
            self.model = YOLO(model_path)

    def predict(self, image_path):
        print(f"Running inference on {image_path}")
        results = self.model(image_path)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = self.model.names[cls]
                
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": [x1, y1, x2, y2]
                })
        
        return detections
