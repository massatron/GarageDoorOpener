import RPi.GPIO as GPIO
   
class DoorSensor:
    def __init__(self, gpioPin):
        self.gpioPin = gpioPin
        GPIO.setup(gpioPin, GPIO.IN, GPIO.PUD_UP)
    
    def is_magnet_aligned(self):
        #print(f"GPIO input for closed sensor (pin {self.gpioPin}): {GPIO.input(self.gpioPin)}")
        return (GPIO.input(self.gpioPin) == GPIO.LOW)