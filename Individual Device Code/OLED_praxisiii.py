import time
import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# Input and Output GPIO Pins
OLED_ADDR = 0x3C
OLED_HEIGHT = 64
OLED_WIDTH = 128
### DOUBLE CHECK ALL PINOUTS
OLED_SDA_PIN = board.GP10
OLED_SCL_PIN = board.GP11

#OLED
displayio.release_displays()

# Initialize OLED display
displayio.release_displays()
i2c_oled = busio.I2C(scl=OLED_SCL_PIN, sda=OLED_SDA_PIN)
display_bus = displayio.I2CDisplay(i2c_oled, device_address=OLED_ADDR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=OLED_WIDTH, height=OLED_HEIGHT)

#i2c_sensor = busio.I2C(scl=board.GP3, sda=board.GP2)
#bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c_sensor, address=0x76)
#sht30 = adafruit_sht31d.SHT31D(i2c_sensor, address=0x44)

while True:
    #print("Humidity: {:.2f} %".format(sht30.relative_humidity))
    print("Humidity: 0%")

    # Make the display context
    fontscale = 10

    # Draw a label
    #text = "Humi (%): {:.2f}".format(sht30.relative_humidity)
    #text = "Humi: 0%"
    #text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group = displayio.Group()
    #text_group.append(text_area)

    text = "ENVIRONMENT SENSOR"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Temp (C): 25C"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)

    text = "Humi (%): 0%"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=30)
    text_group.append(text_area)

    text = "Pres (hPa): Lots"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=43)
    text_group.append(text_area)

    text = "Alti (m): Very High"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=56)
    text_group.append(text_area)

    display.show(text_group)

    time.sleep(2)

