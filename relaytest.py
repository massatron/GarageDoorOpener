from door import DoorRelay
import time
from appSettings import AppSettings
import RPi.GPIO as GPIO

try:
    print(" Control + C to exit Program")
    
    settings = AppSettings("doorSettings")
    relay_pin = int(settings.get_values_for_keys("relay pin")[0])

    # five toggles with 1s delays
    relay = DoorRelay(relay_pin)
    relay.toggle(1,5)

    #turn on and off with 2s delay
    relay.turn_on()
    time.sleep(2)
    relay.turn_off()

    #turn on and off with .5s delay
    relay.turn_on()
    time.sleep(.5)
    relay.turn_off()

    # five toggles with .3s delays
    relay.toggle(.3, 5)
    
except KeyboardInterrupt:     # Stops program when "Control + C" is entered
    print("Stopped by user")
finally:
    GPIO.cleanup() 