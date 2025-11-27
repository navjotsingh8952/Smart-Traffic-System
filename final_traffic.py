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
    print(f"[LCD] {side}: {color}, Timer: {sec:02d}s")


def calculate_green_time(vehicle_count, ambulance):
    print(f"[INFO] Calculating green time → vehicles={vehicle_count}, ambulance={ambulance}")

    if ambulance:
        print("🚨 Ambulance detected → GREEN TIME BOOST (20 + 20)")
        return 40

    if vehicle_count < 5:
        print("[GREEN] Low traffic → 20 sec")
        return 20
    elif vehicle_count < 15:
        print("[GREEN] Medium traffic → 35 sec")
        return 35
    else:
        print("[GREEN] High traffic → 50 sec")
        return 50


def get_counts_api():
    print("[API] Fetching ambulance & vehicle values...")

    try:
        import requests
        url = "https:/projectmakerschn.in/api/get_values.php?id=38"

        response = requests.request("GET", url)
        print("[API] Raw response:", response.text)

        data = response.json()
        vehicle = int(data["field1"])
        ambulance = data["field2"] == "True"

        print(f"[API] Parsed → vehicle={vehicle}, ambulance={ambulance}")
        return vehicle, ambulance

    except Exception as e:
        print("[ERROR] API read failed:", e)
        return 0, False


def side_A_cycle():
    print("\n========== SIDE A START ==========")

    vehicle_count, ambulance = get_counts_api()
    print(f"[SIDE A] Inputs → Vehicle={vehicle_count}, Ambulance={ambulance}")

    green = calculate_green_time(vehicle_count, ambulance)
    print(f"[SIDE A] Final green time = {green} sec\n")

    GPIO.output(A_GREEN, 1)
    GPIO.output(A_RED, 0)

    for t in reversed(range(green)):
        show_lcd("SIDE A", "GREEN", t)
        time.sleep(1)

    GPIO.output(A_GREEN, 0)
    GPIO.output(A_RED, 1)
    print("[SIDE A] Completed.\n")


def side_B_cycle():
    print("\n========== SIDE B START ==========")

    green = calculate_green_time(0, False)
    print(f"[SIDE B] Normal green time = {green} sec\n")

    GPIO.output(A_RED, 1)

    for t in reversed(range(green)):
        vehicle_count, ambulance = get_counts_api()

        if ambulance:
            print("[SIDE B] 🚨 Ambulance detected during SIDE B → Switching to SIDE A immediately")
            return

        show_lcd("SIDE B", "GREEN", t)
        time.sleep(1)

    print("[SIDE B] Completed.\n")


if __name__ == "__main__":
    try:
        print("🚦 Smart Traffic System Started")
        while True:
            side_A_cycle()
            side_B_cycle()

    except KeyboardInterrupt:
        lcd.clear()
        GPIO.cleanup()
        print("Program ended by user.")
