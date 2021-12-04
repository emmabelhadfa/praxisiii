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
from adafruit_motor import stepper
import adafruit_displayio_ssd1306

# Input and Output GPIO Pins
OLED_ADDR = 0x3C
OLED_HEIGHT = 64
OLED_WIDTH = 128
### DOUBLE CHECK ALL PINOUTS
OLED_SDA_PIN = board.GP0
OLED_SCL_PIN = board.GP1
SONAR_TRIG_PIN = board.GP12
SONAR_ECHO_PIN = board.GP11
SOIL_SENS_PIN = board.GP26
INPUT_BUTTON_PIN = board.GP8
EMERG_BUTTON_PIN = board.GP9
# LED Outputs
GREEN_LED_PIN = board.GP13
YELLOW_LED_PIN = board.GP14
RED_LED_PIN = board.GP15
# Coil pins for stepper motor DOUBLE CHECK THIS
COIL_PIN_1 = board.GP21  # IN1
COIL_PIN_2 = board.GP20  # IN2
COIL_PIN_3 = board.GP19  # IN3
COIL_PIN_4 = board.GP18  # IN4

# Working values
distance = None  # Measured distance
calibrated = False  # State of calibration
calibration = None  # Calibrated distance
recommend = None  # Dryness recommendation
clean_dist = 10  # Distance in cm to leave soil sensor exposed for cleaning
supress_errors=True

# Initialize OLED display
displayio.release_displays()
i2c_oled = busio.I2C(scl=OLED_SCL_PIN, sda=OLED_SDA_PIN)
display_bus = displayio.I2CDisplay(i2c_oled, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Initialize LED
led_red = digitalio.DigitalInOut(RED_LED_PIN)
led_red.direction = digitalio.Direction.OUTPUT
led_red.value = False
led_green = digitalio.DigitalInOut(GREEN_LED_PIN)
led_green.direction = digitalio.Direction.OUTPUT
led_green.value = False
led_yellow = digitalio.DigitalInOut(YELLOW_LED_PIN)
led_yellow.direction = digitalio.Direction.OUTPUT
led_yellow.value = False

# Initialize ultrasonic sensor-related IO, variables, buttons, and sensor
led_board = digitalio.DigitalInOut(board.LED)
led_board.direction = digitalio.Direction.OUTPUT

button = digitalio.DigitalInOut(INPUT_BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # Set the internal resistor to pull-up

emergency_stop = digitalio.DigitalInOut(EMERG_BUTTON_PIN)
emergency_stop.direction = digitalio.Direction.INPUT
emergency_stop.pull = digitalio.Pull.UP  # Set the internal resistor to pull-up

sonar = adafruit_hcsr04.HCSR04(trigger_pin=SONAR_TRIG_PIN, echo_pin=SONAR_ECHO_PIN)

# Initialize soil sensor
soil_sens = analogio.AnalogIn(SOIL_SENS_PIN)

# Initialize motor
coils = (
    digitalio.DigitalInOut(COIL_PIN_1),
    digitalio.DigitalInOut(COIL_PIN_2),
    digitalio.DigitalInOut(COIL_PIN_3),
    digitalio.DigitalInOut(COIL_PIN_4),
)

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

motor = stepper.StepperMotor(coils[0], coils[1], coils[2], coils[3], microsteps=None)

# Soil sensor functions
def volts_to_percent(volts):
    """Converts raw capacitive soil moisture sensor data to percentage.

    Assumes linear relationship between max and min voltage readings.

    :return: Moisture content as percentage
    :rtype: Float
    """
    # Sensor Reference Values
    vref = 3.3
    arid = 38000.0  # 1.913V
    sodden = 22000.0  # 1.108V
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
    print(cap_raw)
    cap_percent = volts_to_percent(cap_raw)
    return cap_percent


# OLED and LED functions
def display_result_oled(measurement, recommend, display_device):
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

    # display_device.clear()
    display_device.show(text_group)

    return


def display_result_LED(
    output_mode, led_red, led_green, button
):  # 0 good, 1 reject, else problem
    if output_mode == 1:
        led_green.value = True
    elif output_mode == 0:
        led_red.value = True

    while button.value == True:
        pass

    led_green.value = False
    led_red.value = False
    return


# Motor functions
def extend_sensor(dist_cm, motor, emergency_stop):
    DELAY = 0.01
    ROT_CONST = 0  # CALIBRATE THIS (steps/cm)

    calib_steps = round(dist_cm * ROT_CONST)
    dist_travelled = 0
    curr_steps = 0

    for step in range(calib_steps):
        motor.onestep()  # need to experiment with modes
        curr_steps += 1
        dist_travelled += 1 / ROT_CONST  # (1 / (steps/cm))
        time.sleep(DELAY)
        if not emergency_stop.value:
            return (-1, dist_travelled)  # return -1 for interrupted extension
    return (0, dist_travelled)  # return zero for successful extension


def retract_sensor(dist_cm, motor, emergency_stop):
    DELAY = 0.01
    ROT_CONST = 0  # CALIBRATE THIS (steps/cm)

    calib_steps = round(dist_cm * ROT_CONST)
    dist_travelled = 0
    curr_steps = 0

    for step in range(calib_steps):
        motor.onestep(direction=stepper.BACKWARD)  # need to experiment with modes
        curr_steps += 1
        dist_travelled += 1 / ROT_CONST  # (1 / (steps/cm))
        time.sleep(DELAY)
        if not emergency_stop.value:
            return (-1, dist_travelled)  # return -1 for interrupted extension
    return (0, dist_travelled)  # return zero for successful extension


# System functions
def calibrate_device(sonar_sens):
    dist1 = sonar_sens.distance
    time.sleep(2)
    dist2 = sonar_sens.distance
    time.sleep(2)
    dist3 = sonar_sens.distance
    print(dist1, dist2, dist3)

    mean = (dist1 + dist2 + dist3) / 3

    SD = (((dist1 - mean) ** 2 + (dist2 - mean) ** 2 + (dist3 - mean) ** 2) / 2) ** 0.5

    # Check the standard deviation of the measurements to check if there was an erroneous measurement
    if SD > 5:
        # Return a distance of 1111 to signify a calibration error (SD of measurements too high)
        calibration = -1
        return calibration
    elif mean >= 45:
        # Return a distance of 1111 to signify a calibration error (platform distance exceeds cable carrier length)
        calibration = -1
        return calibration
    else:
        calibration = mean
        return calibration


def sample_dist(sonar_sens, calib_dist):
    SAFE_DIST = 0  # Minimum depth of a sample container to ensure safe sampling
    INSERT_DIST = 0

    dist1 = sonar_sens.distance
    time.sleep(2)
    dist2 = sonar_sens.distance
    time.sleep(2)
    dist3 = sonar_sens.distance

    mean = (dist1 + dist2 + dist3) / 3

    SD = (((dist1 - mean) ** 2 + (dist2 - mean) ** 2 + (dist3 - mean) ** 2) / 2) ** 0.5

    # Check the standard deviation of the measurements to check if there was an erroneous measurement
    if SD > 3:
        # Return a distance of 1111 to signify a distance measurement error (SD of measurements too high)
        dist = -1
        return dist
    elif mean < (calib_dist - SAFE_DIST):
        # Return a distance of 2222 to signify no sample provided (gh)
        dist = -2
        return dist
    elif mean > (calib_dist):
        # Return a distance of 1111 to signify a distance measurement error (SD of measurements too high)
        dist = -1
        return dist
    else:
        dist = mean + INSERT_DIST
        return dist


def calib_error(display_device, button, yellow_led):
    text_group = displayio.Group()
    print("ERROR: Calibration Error")
    text = "ERROR: Calibration Error"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Press INPUT to proceed. . .%"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)
    # display_device.clear()
    display_device.show(text_group)

    yellow_led.value = True

    while button.value == True:
        pass

    # display_device.clear()
    yellow_led.value = False

    return


def sample_height_error(display_device, button, yellow_led):
    text_group = displayio.Group()

    print("ERROR: Sample Height Error")
    text = "ERROR: Sample Height Error"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Press INPUT to proceed. . .%"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)
    # display_device.clear()
    display_device.show(text_group)

    yellow_led.value = True

    while button.value == True:
        pass

    # display_device.clear()
    yellow_led.value = False

    return


def no_sample_error(display_device, button, yellow_led):
    text_group = displayio.Group()

    print("ERROR: No Sample")
    text = "ERROR: No Sample"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Press INPUT to proceed. . .%"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)
    # display_device.clear()
    display_device.show(text_group)

    yellow_led.value = True

    while button.value == True:
        pass

    # display_device.clear()
    yellow_led.value = False

    return


def emerg_stop_err(display_device, button, emergency_stop, yellow_led):
    text_group = displayio.Group()

    print(text="EMERGENCY STOP")
    text = "EMERGENCY STOP"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Press INPUT and EMERG_STOP to proceed. . .%"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)
    # display_device.clear()
    display_device.show(text_group)

    yellow_led.value = True

    while button.value == True or emergency_stop.value == True:
        pass

    # display_device.clear()
    yellow_led.value = False

    return


def cleaning_prompt(display_device, button):

    text_group = displayio.Group()

    print("Gently wipe down moisture sensor probe")
    text = "Gently wipe down moisture sensor probe"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
    text_group.append(text_area)

    text = "Press INPUT to proceed. . .%"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
    text_group.append(text_area)
    # display_device.clear()
    display_device.show(text_group)

    while button.value == True:
        pass

    # display_device.clear()
    return


while True:
    led_green.value = False
    led_yellow.value = False
    led_red.value = False

    text_group = displayio.Group()

    if calibrated == False:
        print("Platform depth not calibrated! Press Button for 5 sec to calibrate.")

        # Send to OLED
        text = "Platform depth not calibrated!"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=4)
        text_group.append(text_area)

        text = "Hold input for 5 sec to calibrate"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=17)
        text_group.append(text_area)

    # Display awaiting input message
    print("Awaiting Input. Press button to test dryness...")
    # Send to OLED
    if calibrated == False:
        y_pos = 36
    else:
        y_pos = 4
    text = "Press input to test dryness..."
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=y_pos)
    text_group.append(text_area)
    # display.clear()
    display.show(text_group)

    # Stay in this while loop until the main input is pressed to avoid constantly refreshing the screen
    while button.value == True:
        pass

    # LED serves as activation light
    led_board.value = not button.value

    if button.value == False:
        just_calibrated = False
        # Record timestamp of button press
        time_pressed = time.monotonic()

        while button.value == False:
            time_released = time.monotonic()
            elapsed = time_released - time_pressed

            # If the button held for >=5 seconds, calibrate the machine
            if elapsed >= 5 and just_calibrated == False:
                print("Calibrating platform depth...")
                calibrating_group = displayio.Group()
                cal_main_text = "Calibrating platform depth"
                cal_main_text_area = label.Label(
                    terminalio.FONT, text=cal_main_text, color=0xFFFFFF, x=0, y=4
                )
                calibrating_group.append(cal_main_text_area)
                # display.clear()
                display.show(calibrating_group)

                calibration = calibrate_device(sonar)
                # Check for calibration errors
                if calibration == -1 and not supress_errors:
                    calib_error(display, button, led_yellow)
                else:
                    calibrated = True
                    just_calibrated = True  # Change to true to avoid re-calibrating
                    print("Calibrated distance: {:.3f} cm".format(calibration))
                    cal_success_group = displayio.Group()
                    cal_success_text = "Calibrated distance: {:.3f} cm".format(
                        calibration
                    )
                    cal_success_text_area = label.Label(
                        terminalio.FONT, text=cal_success_text, color=0xFFFFFF, x=0, y=4
                    )
                    cal_success_group.append(cal_success_text_area)
                    # display.clear()
                    display.show(cal_success_group)
                    time.sleep(3)

        if elapsed < 5:
            # Reset distance prior to measurement
            distance = None
            print("Measuring distance")
            measuring_group = displayio.Group()
            measuring_main_text = "Testing Moisture Content"
            measuring_main_text_area = label.Label(
                terminalio.FONT, text=measuring_main_text, color=0xFFFFFF, x=0, y=4
            )
            measuring_group.append(measuring_main_text_area)
            ##display.clear()
            display.show(measuring_group)

            distance = sample_dist(sonar, calibration)

            # Check for distance measurement errors
            if distance == -1 and not supress_errors:
                sample_height_error(display, button, led_yellow)
            elif distance == -2 and not supress_errors:
                no_sample_error(display, button, led_yellow)
            else:
                # Extend sample by that distance
                (status, dist_travelled) = extend_sensor(
                    distance, motor, emergency_stop
                )
                status = 0
                if status == -1:
                    emerg_stop_err(display, button, emergency_stop, led_yellow)
                    retract_dist = distance - dist_travelled
                    # This part can get recursive... maybe modify this and improve it if possible
                    (status, distance_travelled) = retract_sensor(
                        retract_dist, motor, emergency_stop
                    )
                else:
                    soil_moisture = measure_soil(soil_sens)
                    print(soil_moisture)
                    if soil_moisture > 22:
                        recommend = 0
                    else:
                        recommend = 1
                    display_result_oled(soil_moisture, recommend, display)
                    display_result_LED(recommend, led_red, led_green, button)
                    """
                    dist_to_clean = distance - clean_dist
                    (status, dist_travelled) = retract_sensor(dist_to_clean, motor, emergency_stop)
                    if status == -1:
                        emerg_stop_err(display, button, emergency_stop, led_yellow)
                        retract_dist = distance - dist_travelled
                        # This part can get recursive... maybe modify this and improve it if possible
                        (status, distance_travelled) = retract_sensor(retract_dist, motor, emergency_stop)
                    cleaning_prompt(display, button)
                    (status, dist_travelled) = retract_sensor(clean_dist, motor, emergency_stop)
                    if status == -1:
                        emerg_stop_err(display, button, emergency_stop, led_yellow)
                        retract_dist = distance - dist_travelled
                        # This part can get recursive... maybe modify this and improve it if possible
                        (status, distance_travelled) = retract_sensor(retract_dist, motor, emergency_stop)
                    """
