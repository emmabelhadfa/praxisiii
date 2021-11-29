# Import libraries
import time
import random
import math
import gc

import board
import digitalio
import analogio
import terminalio
import busio

SOIL_SENS_PIN = board.GP26

soil_sens = analogio.AnalogIn(SOIL_SENS_PIN)

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

while True:

    cap_raw = get_value(soil_sens)
    cap_percent = volts_to_percent(cap_raw)
    print("Raw Measurement: {:.3f} V\n Percent Measurement: {:.3f} %".format(cap_raw, cap_percent))
    time.sleep(2)