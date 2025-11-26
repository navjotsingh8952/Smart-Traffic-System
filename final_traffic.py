import time

import RPi.GPIO as GPIO

from lcd_i2c import LCD

GPIO.setmode(GPIO.BCM)

# ---------- LED PINS ----------
A_RED, A_GREEN = 20, 21

for p in [A_RED, A_GREEN]:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

# ---------- LCD ----------
lcd = LCD()


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


def get_counts():
    log_file = "detection_log.txt"

    try:
        # Read the last non-empty line
        with open(log_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            return 0, False

        last = lines[-1]  # example: "2025-11-27 03:45:22 | Vehicle: 11 | Ambulance: True"

        # --- Parse vehicle count ---
        parts = last.split("|")
        vehicle_part = parts[1].strip()  # "Vehicle: 11"
        ambulance_part = parts[2].strip()  # "Ambulance: True"

        vehicle_count = int(vehicle_part.split(":")[1].strip())
        ambulance = ambulance_part.split(":")[1].strip().lower() == "true"

        return vehicle_count, ambulance

    except FileNotFoundError:
        # If no log file exists yet
        return 0, False

    except Exception as e:
        print("Error reading log:", e)
        return 0, False


def side_A_cycle():
    car_count, ambulance = get_counts()
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

    try:
        while True:
            side_A_cycle()
            side_B_cycle()

    except KeyboardInterrupt:
        lcd.clear()
        GPIO.cleanup()
        print("Program ended.")
