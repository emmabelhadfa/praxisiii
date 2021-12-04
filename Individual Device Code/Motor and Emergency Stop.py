import time
import board
import digitalio
from adafruit_motor import stepper

EMERG_BUTTON_PIN = board.GP9
# Coil pins for stepper motor DOUBLE CHECK THIS
COIL_PIN_1 = board.GP21 #IN1
COIL_PIN_2 = board.GP20 #IN2
COIL_PIN_3 = board.GP19 #IN3
COIL_PIN_4 = board.GP18 #IN4

emergency_stop = digitalio.DigitalInOut(EMERG_BUTTON_PIN)
emergency_stop.direction = digitalio.Direction.INPUT
emergency_stop.pull = digitalio.Pull.UP

coils = (digitalio.DigitalInOut(COIL_PIN_1),digitalio.DigitalInOut(COIL_PIN_2),digitalio.DigitalInOut(COIL_PIN_3),digitalio.DigitalInOut(COIL_PIN_4))

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

motor = stepper.StepperMotor(coils[0], coils[1], coils[2], coils[3], microsteps=None)

def extend_sensor(calibrated_steps, motor, emergency_stop):
    DELAY = 0.01
    for step in range(calibrated_steps):
        motor.onestep()   # need to experiment with modes
        time.sleep(DELAY)
        if not emergency_stop.value:
            return -1  # return -1 for interrupted extension
    return 0  # return zero for successful extension

def retract_sensor(motor):  # should this take a distance as an input?
    DELAY = 0.01
    MAX_STEPS=200  # CHANGE! Arbitrary value
    for step in range(MAX_STEPS):  # need to determine whether to use fixed distance and what distance is
        motor.onestep(direction=stepper.BACKWARD)
        time.sleep(DELAY)



