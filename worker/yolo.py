class YoloModel:
    def __init__(self):
        print("Loading YOLO model...")
        # from ultralytics import YOLO
        # self.model = YOLO("yolov8n.pt")
        pass

    def predict(self, image_path):
        print(f"Running inference on {image_path}")
        # results = self.model(image_path)
        # return results[0].tojson()
        return {"detected": ["pid_diagram", "instrument"], "confidence": 0.95}
