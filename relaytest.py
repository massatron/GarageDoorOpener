from door import DoorRelay
import time

try:
    print(" Control + C to exit Program")

    # five toggles with 1s delays
    relay = DoorRelay(7)
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
    relay = DoorRelay(7)
    relay.toggle(.3, 5)
    
except KeyboardInterrupt:     # Stops program when "Control + C" is entered
  GPIO.cleanup()               # Turns OFF all relay switches
