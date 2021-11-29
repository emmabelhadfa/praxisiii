import board
import busio
import adafruit_ssd1306

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3d)
oled.fill(0)
oled.text('Humidity: 0%', 0, 0)
oled.show()