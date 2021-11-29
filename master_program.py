### ESC204 - Praxis III: Team 101D master code for electromechanical moisture-content sensing device
import board
import analogio
import busio
import digitalio
import displayio
import terminalio
import time
import adafruit_hcsr04
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# Input and Output GPIO Pins
OLED_SCL_PIN = board.GP5
OLED_SDA_PIN = board.GP4
ULTRA_TRIG_PIN = board.GP2
ULTRA_ECHO_PIN = board.GP3
SOIL_SENS_PIN = board.GP26
INPUT_BUTTON_PIN = board.GP18
EMERG_BUTTON_PIN = ??? #FILL THIS IN
# add in motor pins

# Initialize OLED display
displayio.release_displays()
i2c_oled = busio.I2C(scl=OLED_SCL_PIN, sda=OLED_SDA_PIN)
display_bus = displayio.I2CDisplay(i2c_oled, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)