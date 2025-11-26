# lcd_i2c.py
# Simple wrapper for 16x2 I2C LCD

from RPLCD.i2c import CharLCD


class LCD:
    def __init__(self):
        # Adjust address and cols/rows according to your LCD
        self.lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

    def clear(self):
        self.lcd.clear()

    def print_line(self, line, text):
        self.lcd.cursor_pos = (line, 0)
        self.lcd.write_string(text.ljust(16))
