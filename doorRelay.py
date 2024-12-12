import RPi.GPIO as GPIO
import time

class DoorRelay:
    
    #initialize relay switch on given pin
    def __init__(self, gpioPin):
        self.gpioPin = gpioPin
        GPIO.setup(gpioPin, GPIO.OUT)
        GPIO.output(gpioPin, GPIO.HIGH)        

    #turn the relay switch on
    def turn_on(self):
        GPIO.output(self.gpioPin, GPIO.LOW)   # turns the first relay switch ON
    
    #turn the relay switch off
    def turn_off(self):
        GPIO.output(self.gpioPin, GPIO.HIGH)  # turns the first relay switch OFF
    
    #turns the relay switch on and off the given number of times
    #with defined delay between operations
    def toggle(self, delay_secs = .5 , no_times =1):
        loop = 0
        while loop < no_times:
            self.turn_on()
            time.sleep(delay_secs)
            self.turn_off()
            time.sleep(delay_secs)
            loop = loop + 1
            
