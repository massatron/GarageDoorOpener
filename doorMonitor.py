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
    def __init__(self, door_log_file):
        self.get_init_values()
        self.door_log = door_log_file
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        #print (self.relay_pin, self.closed_pin, self.open_pin, self.open_min_warn, self.move_sec_warn)
        self.door = Door.create_instance(self.relay_pin, self.closed_pin, self.open_pin, self.open_min_warn, self.move_sec_warn)

    def get_init_values(self):
        settings = AppSettings("doorSettings")
        try:
            settings_values = settings.get_values_for_keys(["relay pin", "closed door sensor pin", "open door sensor pin", "warn when open for minutes", "warn when moving for secs"])

            # Mandatory setting: relay_pin
            self.relay_pin = int(settings_values[0]) if len(settings_values) > 0 and settings_values[0].isdigit() else None
            if self.relay_pin is None:
                raise ValueError("Relay pin configuration is missing or invalid.")

            # Optional settings with defaults
            self.closed_pin = int(settings_values[1]) if len(settings_values) > 1 and settings_values[1].isdigit() else default_closed_pin_value
            self.open_pin = int(settings_values[2]) if len(settings_values) > 2 and settings_values[2].isdigit() else default_open_pin_value
            self.open_min_warn = int(settings_values[3]) if len(settings_values) > 3 and settings_values[3].isdigit() else default_open_min_warn
            self.move_sec_warn = int(settings_values[4]) if len(settings_values) > 4 and settings_values[4].isdigit() else default_move_sec_warn
            
        except ValueError as e:
            print(f"Error in settings configuration: {e}")
            raise 
    
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
    def create_instance(cls, start = False):
        
        settings = AppSettings("doorSettings")
        log_file = settings.get_values_for_keys("log file")[0]
        door_log = DoorLogFile(log_file)
        monitor = cls(door_log)

        if start:
            monitor.start()
        
        return monitor
   
