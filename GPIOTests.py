import RPi.GPIO as GPIO
import time

BTN_PIN = 16 # Pin number of button
LED_PIN = 25

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

GPIO.setup(BTN_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

while True:
    if GPIO.input(BTN_PIN) == 0 :
        GPIO.output(LED_PIN, 0)
    else                        :
        GPIO.output(LED_PIN, 1)

    time.sleep(0.1)