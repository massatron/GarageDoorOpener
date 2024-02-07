import os
import RPi.GPIO as GPIO
import time
from door import *
from appSettings import AppSettings

class DoorLogFile:
    #log file should be in the same directory as this class file
    def __init__(self, file_name):
        self.file_name = file_name
        
    def check_file_size(self, file_name, max_size_bytes=1024):
        try:
            # Get the size of the file
            file_stat = os.stat(file_name)
            file_size = file_stat[6] 
            
            if file_size > max_size_bytes:
                # Open the file in write mode to truncate its contents
                with open(file_name, 'w') as file:
                    file.truncate()
                    print("File {} flushed due to size exceeding {} bytes.".format(file_name, max_size_bytes))
                    
        except OSError as e:
            print("Error DoorLogFile.check_file_size({}):".format(file_name), e)
        
    def get_current_date_time_formatted(self):
        now = time.localtime()
        date = "{}-{}-{} {}:{}".format(now[0], now[1], now[2], now[3], now[4])
        return date

    def file_exists(self, file_name):
        return file_name in os.listdir()

    def append(self, message):
        log_message = self.get_current_date_time_formatted() + " : " + message
        
        try:
            if not self.file_exists(self.file_name):
                with open(self.file_name, 'w') as file:
                    file.write(log_message + '\n')
            else:
                self.check_file_size(self.file_name) 
                with open(self.file_name, 'a') as file:
                    file.write(log_message + '\n')
        
        except OSError as e:
            print(f"OS error occurred: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
        except Exception as e:
            # This is a catch-all for any other exceptions
            print(f"An unexpected error occurred: {e}")
                

class DoorMonitor:
    def __init__(self, door, door_log_file):
        self.door_log = door_log_file
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        self.door = door
    
    def get_current_door_state(self):
        return self.door.get_current_state_string()
    
    #Runs DoorMonitor continously.
    def start(self):
        print(" Control + C to exit Program")
        message = "Starting Monitor"
        self.door_log.append(message)

        try:
            while True:
                time.sleep(1)
                change = self.door.evaluate_door_state()
                if(change):
                    self.door_log.append(self.door.state_change_message)
                if not self.door.is_closed():
                    print("open for: ", self.door.seconds_open(), " seconds.")
                if self.door.is_moving():
                    print("moving state for: ", self.door.seconds_moving(), " seconds")

        except ValueError as e:
            self.door_log.append(message)
            print("Error:", e) 
        except KeyboardInterrupt:
            message = "Pogram shutting down - {}".format(get_current_date_time_formatted())
            self.door_log.append(message)
            print(message)
        finally:
            GPIO.cleanup()


    @classmethod
    def create_instance(cls, door_to_monitor = None, start = False):
        
        settings = AppSettings("doorSettings")
        log_file = settings.get_values_for_keys("log file")[0]
        door_log = DoorLogFile(log_file)
        if door_to_monitor is None:
            door = Door.create_instance_from_settings()
            print("door created from settings")
        else:
            door = door_to_monitor
            
        monitor = cls(door, door_log)

        if start:
            monitor.start()
        
        return monitor
   
