import os
import RPi.GPIO as GPIO
import time
from door import *
from appSettings import AppSettings

class DoorLogFile:
    #log file should be in the same directory as this class file
    def __init__(self, file_name):
        self.file_name = file_name
        
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

    def append(message):
        log_message = self.get_current_date_time_formatted() + " : " + message
        
        if not self.file_exists(filename):
            with open(self.filename, 'w') as file:
                file.write(log_message + '\n')
        else:
            self.check_file_size(filename) 
            with open(self.filename, 'a') as file:
                file.write(log_message + '\n')
                

class DoorMonitor:
    def __init__(self, door_log_file):
        settings = AppSettings("doorSettings")
        self.relay_pin, self.closed_pin, self.open_pin, self.open_min_warn, self.move_sec_warn = \
        settings.get_values_for_keys(["relay pin", "closed door sensor pin", "open door sensor pin", "warn when open for minutes", "warn when moving for secs"])
        self.door_log = door_log_file
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        self.door = Door.create_instance(self.relay_pin, self.closed_pin, self.open_pin, self.open_min_warn, self.move_sec_warn)

    def start(self):
        print(" Control + C to exit Program")
        message = "Starting Monitor"
        door_log.append(message)

        try:
            while 1 >= 0:
                time.sleep(1)
                change = door.evaluate_door_state()
                if(change):
                    self.door_log.append(door.state_change_message)
                if not door.is_closed():
                    print("open for: ", door.seconds_open(), " seconds.")
                if door.is_moving():
                    print("moving state for: ", door.seconds_moving(), " seconds")

        except ValueError as e:
            self.door_log.append(message)
            print("Error:", e) 
        except KeyboardInterrupt:
            message = "Pogram shutting down - {}".format(get_current_date_time_formatted())
            self.door_log.append(message)
            print(message)
            GPIO.cleanup()


    @classmethod
    def create_instance(cls, start = False):
        
        settings = AppSettings("doorSettings")
        log_file = settings.get_values_for_keys(["log file"])
        door_log = DoorLogFile(log_file)
        monitor = cls(door_log)

        if start:
            monitor.start()
        
        return monitor
   
