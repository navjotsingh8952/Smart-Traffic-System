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


def send_output(vehicle_count, ambulance):
    import requests
    url = f"https:/projectmakerschn.in/api/set_values.php?field1={vehicle_count}&field2={ambulance}&id=38&field3="
    response = requests.request("GET", url)
    print(response.text)


def get_counts(cap):
    """Return vehicle count + ambulance boolean."""
    ret, frame = cap.read()
    if not ret:
        return 0, False

    results = model.predict(frame, conf=CONF, device="cpu")

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

    r = results[0]
    annotated = r.plot()
    cv2.imshow("Webcam Detection", annotated)
    print(f"Vehicle: {vehicle_count}, Ambulance: {ambulance}")

    # append to file
    log_output(vehicle_count, ambulance)
    send_output(vehicle_count, ambulance)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
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
