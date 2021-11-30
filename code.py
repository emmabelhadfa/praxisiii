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
SONAR_TRIG_PIN = board.GP2
SONAR_ECHO_PIN = board.GP3
SOIL_SENS_PIN = board.GP26
INPUT_BUTTON_PIN = board.GP18
EMERG_BUTTON_PIN = ??? #FILL THIS IN
# Coil pins for stepper motor DOUBLE CHECK THIS
COIL_PIN_1 = board.GP14
COIL_PIN_2 = board.GP15
COIL_PIN_3 = board.GP16
COIL_PIN_4 = board.GP17

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

sonar = adafruit_hcsr04.HCSR04(trigger_pin=SONAR_TRIG_PIN, echo_pin=SONAR_ECHO_PIN)

# Initialize soil sensor
soil_sens = analogio.AnalogIn(SOIL_SENS_PIN)

# Soil sensor functions
def volts_to_percent(volts):
    """Converts raw capacitive soil moisture sensor data to percentage.
    
    Assumes linear relationship between max and min voltage readings.
    
    :return: Moisture content as percentage
    :rtype: Float
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
    """Returns the average measured value from an analog input over 500 samples.
    
    :return: Average analog moisture content reading
    :rtype: Int
    """
    return sum([ain.value for _ in range(samples)]) / samples

def measure_soil(sensor):
    """Measures the soil moisture content from a Grove capacitive soil moisture sensor and returns the measured percentage value
    
    :return: Percent soil moisture content 
    :rtype: Float
    """
    cap_raw = get_value(sensor)
    cap_percent = volts_to_percent(cap_raw)
    return cap_percent

def display_result_oled(measurement, recommend, display_io):
    """Displays the measured moisture content value and the drying recommendation on the OLED display given in display_io.

    :return: None
    """
    text_group = displayio.Group()

    text = "AUTOMATED SAWDUST PROCESSOR"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Moisture Content: {:.1f} %".format(measurement)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)

    # Decision tree for recommendation
    if recommend == 0:
        text = "Needs Drying?: NO"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=30)
        text_group.append(text_area)
    elif recommend == 1:
        text = "Needs Drying?: YES"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=30)
        text_group.append(text_area)

    text = "(Press input to continue)"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=56)
    text_group.append(text_area)

    display.show(text_group)

    return

def calibrate_device(sonar_sens):
    print("Calibrating platform depth...")
    calibrating_group = displayio.Group()
    cal_main_text = "Calibrating platform depth"
    cal_main_text_area = label.Label(terminalio.FONT, text=cal_main_text, color=0xFFFFFF, x=0, y=4)
    calibrating_group.append(cal_main_text_area)

    dist1 = sonar_sens.distance
    time.sleep(2)
    dist2 = sonar_sens.distance
    time.sleep(2)
    dist3 = sonar_sens.distance

    calibration = ???? # FIGURE OUT HOW TO ELIMINATE OUTLIERS

    return calibration

while True:
    
    text_group = displayio.Group()

    if calibrated == False and calib_notif_sent == False:
        print("Platform depth not calibrated! Press Button for 5 sec to calibrate.")
        
        # Send to OLED
        text = "Platform depth not calibrated!"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
        text_group.append(text_area)

        text = "Hold input for 5 sec to calibrate"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
        text_group.append(text_area)

        calib_notif_sent = True

    if notif_sent == False:
        print("Awaiting Input. Press button to test dryness...")

        # Send to OLED
        if calibrated == False:
            y_pos = 36
        else:
            y_pos = 4
        text = "Press input to test dryness..."
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=y_pos)
        text_group.append(text_area)

        notif_sent = True

        display.show(text_group)

    # Stay in this while loop until the main input is pressed to avoid constantly refreshing the screen
    while button.value == True:
        pass

    # LED serves as activation light
    led.value = not button.value

    if button.value:
        # Reset notification status
        notif_sent == False
        just_calibrated = False
        # Record timestamp of button press
        time_pressed = time.monotonic()

        while button.value == False:
            time_released = time.monotonic()
            elapsed = time_released - time_pressed

            # If the button held for >=5 seconds, calibrate the machine
            if elapsed >= 5 and just_calibrated == False:
                ### THIS SECTION INCOMPLETE
                calibration = calibrate_device()
                calibrated = True
                just_calibrated = True # Change to true to avoid re-calibrating
                print("Calibrated distance: {:.3f} cm".format(calibration))

        ### INCOMPLETE