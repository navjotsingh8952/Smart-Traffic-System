import argparse
from datetime import datetime

import cv2
from ultralytics import YOLO

# ---------- YOLO ----------
model = YOLO("model/best.pt")
CONF = 0.45
VEHICLE_CLASSES = ["car", "truck", "bike", "rickshaw", "bus"]

LOG_FILE = "detection_log.txt"


def log_output(vehicle_count, ambulance):
    """Append output to a file with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} | Vehicle: {vehicle_count} | Ambulance: {ambulance}\n")


def get_counts(cap):
    """Return vehicle count + ambulance boolean."""
    ret, frame = cap.read()
    if not ret:
        return 0, False

    results = model.predict(frame, conf=CONF)

    vehicle_count = 0
    ambulance = False

    for r in results:
        for box in r.boxes:
            if float(box.conf) < 0.7:
                continue

            cls_id = int(box.cls)
            class_name = r.names[cls_id]

            if class_name == "emergency":
                ambulance = True

            if class_name in VEHICLE_CLASSES:  # FIXED
                vehicle_count += 1

    print(f"Vehicle: {vehicle_count}, Ambulance: {ambulance}")

    # append to file
    log_output(vehicle_count, ambulance)

    return vehicle_count, ambulance


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cam", type=str, help="Camera ID (ex: 0 or rtsp stream)")
    args = parser.parse_args()

    cam_id = args.cam if args.cam is not None else 0

    print(f"Using camera: {cam_id}")
    cap = cv2.VideoCapture(cam_id)

    while True:
        get_counts(cap)
