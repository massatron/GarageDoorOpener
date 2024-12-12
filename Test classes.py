import RPi.GPIO as GPIO
from door import Door
from doorRelay import DoorRelay
from doorState import DoorState
from doorStateTimer import DoorStateTimer
from doorSensor import DoorSensor
from appSettings import AppSettings
import time


# Initialize GPIO
GPIO.setmode(GPIO.BCM)

# Pin assignments
RELAY_PIN = 7
CLOSED_SENSOR_PIN = 18
OPEN_SENSOR_PIN = 16

def test_door_relay():
    print("Testing DoorRelay...")
    relay = DoorRelay(RELAY_PIN)
    
    print("Turning on relay...")
    relay.turn_on()
    time.sleep(1)  # Observe relay behavior
    
    print("Turning off relay...")
    relay.turn_off()
    time.sleep(1)  # Observe relay behavior
    
    print("Toggling relay 3 times...")
    relay.toggle(delay_secs=0.5, no_times=3)
    
    print("DoorRelay test completed.")

def test_door_sensor():
    print("Testing DoorSensor...")
    closed_sensor = DoorSensor(CLOSED_SENSOR_PIN)
    open_sensor = DoorSensor(OPEN_SENSOR_PIN)
    
    print("Closed Sensor Readings:")
    for _ in range(5):
        print(f"Is closed sensor magnet aligned? {closed_sensor.is_magnet_aligned()}")
        time.sleep(1)
    
    print("Open Sensor Readings:")
    for _ in range(5):
        print(f"Is open sensor magnet aligned? {open_sensor.is_magnet_aligned()}")
        time.sleep(1)
    
    print("DoorSensor test completed.")

def test_door_state_timer():
    print("Testing DoorStateTimer...")
    timer = DoorStateTimer(doorstate=DoorState.Open)
    
    print("Initial seconds elapsed:", timer.seconds_from_timestamp())
    print("Initial minutes elapsed:", timer.minutes_from_timestamp())
    
    time.sleep(3)  # Wait 3 seconds
    print("Seconds elapsed after 3 seconds:", timer.seconds_from_timestamp())
    
    timer.set_state_start()
    print("Seconds elapsed after reset:", timer.seconds_from_timestamp())
    
    timer.reset()
    print("Seconds elapsed after full reset:", timer.seconds_from_timestamp())
    
    print("DoorStateTimer test completed.")

def test_door():
    print("Testing Door...")
    relay = DoorRelay(RELAY_PIN)
    closed_sensor = DoorSensor(CLOSED_SENSOR_PIN)
    open_sensor = DoorSensor(OPEN_SENSOR_PIN)
    door = Door(relay, closed_sensor, open_sensor)
    
    print("Initial door state:", door.get_current_state_string())
    print("Seconds open:", door.seconds_open())
    print("Seconds closed:", door.seconds_closed())
    
    print("Opening the door...")
    door.open_the_door()
    time.sleep(10)
    print("Door state after 3 seconds:", door.get_current_state_string())
    print("Seconds opening:", door.seconds_opening())
    
    print("Closing the door...")
    door.close_the_door()
    time.sleep(10)
    print("Door state after 3 seconds:", door.get_current_state_string())
    print("Seconds closing:", door.seconds_closing())
    
    print("Door test completed.")

# Clean up GPIO after testing
def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        print("Starting tests...")
        #test_door_relay()
        #test_door_sensor()
        #test_door_state_timer()
        test_door()
    finally:
        cleanup()
