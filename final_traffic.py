import argparse
import time

import RPi.GPIO as GPIO
import cv2
from ultralytics import YOLO

from lcd_i2c import LCD

GPIO.setmode(GPIO.BCM)

# ---------- LED PINS ----------
A_RED, A_GREEN = 20, 21

for p in [A_RED, A_GREEN]:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

# ---------- LCD ----------
lcd = LCD()

# ---------- YOLO ----------
model = YOLO("model/best.pt")
CONF = 0.45
VEHICLE_CLASSES = ["car", "truck", "bike", "rickshaw", "bus"]


# ✔ ONE function to get BOTH car count + ambulance detection
def get_counts(cap):
    ret, frame = cap.read()
    if not ret:
        print(0, False)
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

            if class_name in [VEHICLE_CLASSES]:
                vehicle_count += 1
    print(f"Vehicle: {vehicle_count}, Ambulance: {ambulance}")
    return vehicle_count, ambulance


def show_lcd(side, color, sec):
    lcd.clear()
    lcd.print_line(0, f"{side}: {color}")
    lcd.print_line(1, f"Timer: {sec:02d}s")
    print(f"{side}: {color}, Timer: {sec:02d}s")


def calculate_green_time(car_count, ambulance):
    if ambulance:
        print("🚨 Ambulance detected → Giving priority!")
        return 20 + 20  # normal 20 + extra 20

    if car_count < 5:
        return 20
    elif car_count < 15:
        return 35
    else:
        return 50


def side_A_cycle(cap):
    car_count = 0
    ambulance = False
    if cap is not None:
        car_count, ambulance = get_counts(cap)
    green = calculate_green_time(car_count, ambulance)

    GPIO.output(A_GREEN, 1)
    GPIO.output(A_RED, 0)

    for t in reversed(range(green)):
        show_lcd("SIDE A", "GREEN", t)
        time.sleep(1)

    GPIO.output(A_GREEN, 0)
    GPIO.output(A_RED, 1)


def side_B_cycle():
    # Side B has no ambulance detection (single camera)
    green = calculate_green_time(0, False)

    GPIO.output(A_RED, 1)

    for t in reversed(range(green)):
        show_lcd("SIDE B", "GREEN", t)
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cam", type=str, help="Camera ID")
    args = parser.parse_args()
    cam_id = args.cam
    cap = None
    if cam_id is not None:
        print("Initialized video")
        cap = cv2.VideoCapture(cam_id)

    try:
        while True:
            side_A_cycle(cap)
            side_B_cycle()

    except KeyboardInterrupt:
        lcd.clear()
        GPIO.cleanup()
        cap.release()
        print("Program ended.")
