import json
import cv2
from flask import Flask, render_template, Response, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# Load YOLOv8 model (replace with your custom weights path if any)
model = YOLO('yolov8x.pt')

# Load component descriptions
with open('components.json', 'r') as f:
    comp_desc = json.load(f)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Shared variable to hold the last detected class
last_detected = {'label': None}

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run detection
        results = model(frame)[0]
        # Draw boxes + labels, track the most confident
        best_conf = 0
        best_label = None

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id]

            # Draw rectangle + text
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)

            # Capture the top confident label
            if conf > best_conf:
                best_conf = conf
                best_label = label

        # Update shared detection
        last_detected['label'] = best_label

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/describe', methods=['POST'])
def describe():
    # Client will send { "question": "..."}
    data = request.get_json()
    label = last_detected.get('label')
    if not label:
        answer = "I can't see any component clearly. Please show it to the camera."
    else:
        # Lookup description
        answer = comp_desc.get(label,
               f"No description found for {label}.")
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)