import time

import RPi.GPIO as GPIO
import cv2
from lcd_i2c import LCD
from ultralytics import YOLO

GPIO.setmode(GPIO.BCM)

# ---------- LED PINS ----------
A_RED, A_GREEN = 2, 4
B_RED, B_GREEN = 17, 22

for p in [A_RED, A_GREEN, B_RED, B_GREEN]:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

# ---------- LCD ----------
lcd = LCD()

# ---------- YOLO ----------
model = YOLO("model/best.pt")
cam = cv2.VideoCapture(0)
CONF = 0.45
VEHICLE_CLASSES = ["car", "truck", "bike", "rickshaw", "bus"]


# ✔ ONE function to get BOTH car count + ambulance detection
def get_counts():
    ret, frame = cam.read()
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

            if class_name in [VEHICLE_CLASSES]:
                vehicle_count += 1
    print(f"Vehicle: {vehicle_count}, Ambulance: {ambulance}")
    return vehicle_count, ambulance


def show_lcd(side, color, sec):
    lcd.clear()
    lcd.print_line(0, f"{side}: {color}")
    lcd.print_line(1, f"Timer: {sec:02d}s")


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


def side_A_cycle():
    car_count, ambulance = get_counts()
    green = calculate_green_time(car_count, ambulance)

    GPIO.output(A_GREEN, 1)
    GPIO.output(B_RED, 1)
    GPIO.output(A_RED, 0)

    for t in reversed(range(green)):
        show_lcd("SIDE A", "GREEN", t)
        time.sleep(1)

    GPIO.output(A_GREEN, 0)
    GPIO.output(A_RED, 1)


def side_B_cycle():
    # Side B has no ambulance detection (single camera)
    green = calculate_green_time(0, False)

    GPIO.output(B_GREEN, 1)
    GPIO.output(A_RED, 1)
    GPIO.output(B_RED, 0)

    for t in reversed(range(green)):
        show_lcd("SIDE B", "GREEN", t)
        time.sleep(1)

    GPIO.output(B_GREEN, 0)
    GPIO.output(B_RED, 1)


try:
    while True:
        side_A_cycle()
        side_B_cycle()

except KeyboardInterrupt:
    lcd.clear()
    GPIO.cleanup()
    print("Program ended.")
