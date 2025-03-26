from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306 # type: ignore
import board
import busio
import time

class Display:
    def __init__(self):
        # OLED Display Setup
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.font = ImageFont.load_default()

        # Clear display at startup
        self.oled.fill(0)
        self.oled.show()

        print("Display init")

    def show_message(self, message, duration=2):
        """ Display a message on the OLED """
        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), message, font=self.font, fill=255)
        self.oled.image(image)
        self.oled.show()
#        time.sleep(duration)

    def clear_display(self):
        """ Clear the OLED screen """
        self.oled.fill(0)
        self.oled.show()