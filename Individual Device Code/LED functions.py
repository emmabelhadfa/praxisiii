import time
import board
import digitalio

# LED Outputs
GREEN_LED_PIN = board.GP13
YELLOW_LED_PIN = board.GP14
RED_LED_PIN = board.GP15

led_red = digitalio.DigitalInOut(RED_LED_PIN)
led_green = digitalio.DigitalInOut(GREEN_LED_PIN)
led_yellow = digitalio.DigitalInOut(YELLOW_LED_PIN)

def led_output(output_mode, led_red, led_green, led_yellow):  # 0 good, 1 reject, else problem
    if output_mode == 0:
        led_green.value=True
    elif output_mode==1:
        led_red.value=True
    else:
        led_yellow.value=True
    time.sleep(5)  # delay for light to be on, must decide behaviour
    led_green.value=False
    led_red.value=False
    led_yellow.value=False
