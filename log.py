import os
import RPi.GPIO as GPIO
import time
from config import (NUMBER_OF_DOORS, SENSORS_PER_DOOR)
from door import *

def check_file_size(filename, max_size_bytes=1024):
    try:
        # Get the size of the file
        file_stat = os.stat(filename)
        file_size = file_stat[6] 
        
        if file_size > max_size_bytes:
            # Open the file in write mode to truncate its contents
            with open(filename, 'w') as file:
                file.truncate()
                print("File {} flushed due to size exceeding {} bytes.".format(filename, max_size_bytes))
                
    except OSError as e:
        print("Error:", e)
    
def get_current_date_time_formatted():
    now = time.localtime()
    date = "{}-{}-{} {}:{}".format(now[0], now[1], now[2], now[3], now[4])
    return date

def file_exists(filename):
    return filename in os.listdir()

def append_log_file(filename, message):
    
    if not file_exists(filename):
        with open(filename, 'w') as file:
            pass
    else:
        check_file_size(filename)
                
    with open(filename, 'a') as file:
        print(message)
        file.write(message + '\n')
            

log_file = 'log.txt'
message = "Program starting - {}".format(get_current_date_time_formatted())
append_log_file(log_file, message)

print(" Control + C to exit Program")
print(" Number of Sensors: " + str(SENSORS_PER_DOOR))

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

door = Door.create_instance(7,18,16,1,1)
time.sleep(1)

try:
    while 1 >= 0:
        time.sleep(1)
        change = door.evaluate_door_state()
        if(change):
            print(door.state_change_message)
        if not door.is_closed():
            print("open for: ", door.seconds_open(), " seconds.")
        if door.is_moving():
            print("moving state for: ", door.seconds_moving(), " seconds")

except ValueError as e:
    append_log_file(log_file, message)
    print("Error:", e) 
except KeyboardInterrupt:
    message = "Pogram shutting down - {}".format(get_current_date_time_formatted())
    append_log_file(log_file, message)
    print(message)
    GPIO.cleanup()
