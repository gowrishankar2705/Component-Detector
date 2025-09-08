from ultralytics import YOLO # type: ignore

# Load a pretrained YOLOv8 model (choose yolov8n/s/m/l/x based on your needs)
model = YOLO('yolov8n.pt')  # 'n' is fastest, 'x' is most accurate

# Train on your dataset
model.train(
    data='custom_data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='component_detector',
    project='runs/train',
    device='cpu'  # use 'cpu' if no GPU
)