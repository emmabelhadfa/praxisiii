import time
import board
import busio
import displayio
import digitalio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import adafruit_bmp280
import adafruit_sht31d.mpy


#OLED
displayio.release_displays()

i2c_oled = busio.I2C(scl=board.GP5, sda=board.GP4)
display_bus = displayio.I2CDisplay(i2c_oled, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64) #changed it to SSD1315

i2c_sensor = busio.I2C(scl=board.GP3, sda=board.GP2)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c_sensor, address=0x76)
sht30 = adafruit_sht31d.SHT31D(i2c_sensor, address=0x44)

while True:
    print("Moisture: {:.2f} %".format(sht30.relative_humidity))

    # Make the display context
    text_group = displayio.Group(max_size=10)

    # Draw a label
    text = "Moisture (%): {:.2f}".format(sht30.relative_humidity)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=30)
    text_group.append(text_area)

    display.show(text_group)

    time.sleep(2)

#LED Lights

# Configure the internal GPIO connected to the red LED as a digital output
ledr = digitalio.DigitalInOut(board.GP17)
ledr.direction = digitalio.Direction.OUTPUT

# Configure the internal GPIO connected to the green LED as a digital output
ledg = digitalio.DigitalInOut(board.GP18)
ledg.direction = digitalio.Direction.OUTPUT

# Configure the internal GPIO connected to the yellow LED as a digital output
ledy = digitalio.DigitalInOut(board.GP19)
ledy.direction = digitalio.Direction.OUTPUT

# Configure the internal GPIO connected to the first button as a digital input
button1 = digitalio.DigitalInOut(board.GP15)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP # Set the internal resistor to pull-up

# Configure the internal GPIO connected to the second button as a digital input
button2 = digitalio.DigitalInOut(board.GP14) 
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP # Set the internal resistor to pull-up

# Configure the internal GPIO connected to the third button as a digital input
button3 = digitalio.DigitalInOut(board.GP13) 
button3.direction = digitalio.Direction.INPUT
button3.pull = digitalio.Pull.UP # Set the internal resistor to pull-up

# Loop so the code runs continuously
while True:
	ledr.value = not button1.value 	# turn on red light if button 1 is pressed
	ledg.value = not button2.value	# turn on green light if button 2 is pressed
    ledy.value = not button3.value	# turn on green light if button 3 is pressed
