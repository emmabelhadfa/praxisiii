# Import libraries needed for blinking the LED
import board
import digitalio
import time
import adafruit_hcsr04

# Configure the internal GPIO connected to the LED as a digital output
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Configure the internal GPIO connected to the button as a digital input
button = digitalio.DigitalInOut(board.GP18)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP # Set the internal resistor to pull-up

notif_sent = False # Console notification boolean for sonar state
calib_notif_sent = False
distance = None # Measured distance
calibrated = False # State of calibration
calibration = None # Calibrated distance

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP2, echo_pin=board.GP3)

while True:
    if calibrated == False and calib_notif_sent == False:
        print("Platform depth not calibrated! Press Button for 5 sec to calibrate.")
        calib_notif_sent = True
        

    if notif_sent == False:
        print("Awaiting Input. Press button to measure distance...")
        notif_sent = True

    # LED serves as activation light
    led.value = not button.value
    
    if button.value == False:
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
                print("Calibrating platform depth...")
                calibration = sonar.distance
                calibrated = True
                just_calibrated = True
                print("Calibrated distance: {:.3f} cm".format(calibration))
        
        if elapsed < 5:
            # Reset distance prior to measurement
            distance = None
            print("Measuring distance")

            distance = sonar.distance
            print("Measured distance: {:.3f} cm".format(distance))
            time.sleep(2)
            if calibrated == False:
                calib_notif_sent = False