import datetime
import time

import RPi.GPIO as GPIO

from lcd_i2c import LCD


# ---------- TIMESTAMP PRINT ----------
def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


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
    log(f"[LCD] {side}: {color}, Timer: {sec:02d}s")


def calculate_green_time(vehicle_count, ambulance):
    log(f"[INFO] Calculating green time → vehicles={vehicle_count}, ambulance={ambulance}")

    if ambulance:
        log("🚨 Ambulance detected → GREEN TIME BOOST (20 + 20)")
        return 40

    if vehicle_count < 5:
        log("[GREEN] Low traffic → 20 sec")
        return 20
    elif vehicle_count < 15:
        log("[GREEN] Medium traffic → 35 sec")
        return 35
    else:
        log("[GREEN] High traffic → 50 sec")
        return 50


def get_counts_api():
    log("[API] Fetching ambulance & vehicle values...")

    try:
        import requests
        url = "https:/projectmakerschn.in/api/get_values.php?id=38"

        response = requests.request("GET", url)
        log(f"[API] Raw response: {response.text}")

        data = response.json()
        vehicle = int(data["field1"])
        ambulance = data["field2"] == "True"

        log(f"[API] Parsed → vehicle={vehicle}, ambulance={ambulance}")
        return vehicle, ambulance

    except Exception as e:
        log(f"[ERROR] API read failed: {e}")
        return 0, False


def side_A_cycle():
    log("\n========== SIDE A START ==========")

    vehicle_count, ambulance = get_counts_api()
    log(f"[SIDE A] Inputs → Vehicle={vehicle_count}, Ambulance={ambulance}")

    green = calculate_green_time(vehicle_count, ambulance)
    log(f"[SIDE A] Final green time = {green} sec\n")

    GPIO.output(A_GREEN, 1)
    GPIO.output(A_RED, 0)

    for t in reversed(range(green)):
        show_lcd("SIDE A", "GREEN", t)
        time.sleep(1)

    GPIO.output(A_GREEN, 0)
    GPIO.output(A_RED, 1)
    log("[SIDE A] Completed.\n")


def side_B_cycle():
    log("\n========== SIDE B START ==========")

    green = calculate_green_time(0, False)
    log(f"[SIDE B] Normal green time = {green} sec\n")

    GPIO.output(A_RED, 1)

    for t in reversed(range(green)):
        vehicle_count, ambulance = get_counts_api()

        if ambulance:
            log("[SIDE B] 🚨 Ambulance detected during SIDE B → Switching to SIDE A immediately")
            return

        show_lcd("SIDE B", "GREEN", t)
        time.sleep(1)

    log("[SIDE B] Completed.\n")


if __name__ == "__main__":
    try:
        log("🚦 Smart Traffic System Started")
        while True:
            side_A_cycle()
            side_B_cycle()

    except KeyboardInterrupt:
        lcd.clear()
        GPIO.cleanup()
        log("Program ended by user.")
