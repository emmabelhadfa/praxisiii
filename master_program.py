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

# Initialize ultrasonic sensor-related IO, variables, and sensor
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

button = digitalio.DigitalInOut(INPUT_BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP # Set the internal resistor to pull-up

notif_sent = False # Console notification boolean for sonar state
calib_notif_sent = False
distance = None # Measured distance
calibrated = False # State of calibration
calibration = None # Calibrated distance

sonar = adafruit_hcsr04.HCSR04(trigger_pin=ULTRA_TRIG_PIN, echo_pin=ULTRA_ECHO_PIN)

# Initialize soil sensor
soil_sens = analogio.AnalogIn(SOIL_SENS_PIN)

# Soil sensor functions
def volts_to_percent(volts):
    """Converts raw capacitive soil moisture sensor data.
    Assumes linear relationship between max and min voltage readings.
    """
    # Sensor Reference Values
    vref = 3.3
    arid = 38000.0 # 1.913V
    sodden = 22000.0 # 1.108V
    range = arid - sodden

    # Calculate
    frac = 1 - ((volts - sodden) / range)
    percent = min(100.0, max(0.0, frac * 100.0))

    return percent

def get_value(ain, samples=500):
    return sum([ain.value for _ in range(samples)]) / samples

def measure_soil(sensor):
    cap_raw = get_value(sensor)
    cap_percent = volts_to_percent(cap_raw)
    return cap_percent