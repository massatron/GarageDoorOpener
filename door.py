import RPi.GPIO as GPIO
import time
from appSettings import AppSettings

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
            

class DoorState:
    Open = 1
    Closed = 2
    Unknown = 3
    Opening = 4
    Closing = 5
    
    def state_string(state):
        if state == 1:
            return "Open"
        if state == 2:
            return "Closed"
        if state == 3:
            return "Unknown"
        if state == 4:
            return "Opening"
        if state == 5:
            return "Closing"
        
        raise ValueError("DoorState value: ", state, " is invalid")
    
class DoorSensor:
    def __init__(self, gpioPin):
        self.gpioPin = gpioPin
        GPIO.setup(gpioPin, GPIO.IN, GPIO.PUD_UP)
    
    def is_magnet_aligned(self):  
        return (GPIO.input(self.gpioPin) == GPIO.HIGH)

class DoorStateTimer:
    
    # time_unit can be "m" for minutes or "s" for seconds. Anything else will be treated as mintues.
    def __init__(self, doorstate):
        self.doorstate = doorstate
        self.set_state_start()
        
    def reset(self):
        self.start_time = None

    def minutes_from_timestamp(self):
        if self.start_time is None:
            return 0
        difference_minutes =self.seconds_from_timestamp() / 60
        return int(difference_minutes)
    
    def seconds_from_timestamp(self):
        if self.start_time is None:
            return 0
        now_stamp = time.mktime(time.localtime())
        difference_secs = (now_stamp - self.start_time)
        return int(difference_secs)
    
    def set_state_start(self):
        self.start_time = time.mktime(time.localtime())

class Door:
    
    def __init__(self, relay_switch, door_sensor_closed=None, door_sensor_open=None, warn_when_open_minutes = 15, warn_when_moving_seconds = 15):
        self.relay_switch = relay_switch
        
        #setup known states
        self.current_state = DoorState.Unknown
        self.last_state = DoorState.Unknown

        #setup door state timer
        self.unknown_state_timer = DoorStateTimer(DoorState.Unknown)
        self.open_state_timer = DoorStateTimer(DoorState.Open)
        self.opening_state_timer = DoorStateTimer(DoorState.Opening)
        self.closed_state_timer = DoorStateTimer(DoorState.Closed)
        self.closing_state_timer = DoorStateTimer(DoorState.Closing)
        
        if door_sensor_closed is None and door_sensor_open is None:
            self.sensors = 0  # No sensors
        elif door_sensor_open is None:
            self.sensors = 1
            self.closed_sensor = door_sensor_closed
        elif door_sensor_closed is None:
            self.sensors = 1
            self.open_sensor = door_sensor_open            
        else:
            self.sensors = 2
            self.closed_sensor = door_sensor_closed
            self.open_sensor = door_sensor_open
        
        self.evaluate_door_state()
    
    # resets all door state timers.
    def reset_state_timers(self):
        self.open_state_timer.reset()
        self.opening_state_timer.reset()
        self.closed_state_timer.reset()
        self.closing_state_timer.reset()
        
    # returns the current state of the door in
    # string format.
    def get_current_state_string(self):
        return DoorState.state_string(self.current_state)
    
    # sets current state to the supplied state and
    # sets the last_state to the current state
    def set_new_state(self, new_state):
        self.last_state = self.current_state
        self.current_state = new_state
    
    def set_unknown_state(self):
        self.set_new_state(DoorState.Unknown)
    
    #probably either opening or closing, but could be stopped in between somewhere
    def set_moving_state(self):
        # Look at previous state to determine in which direction wer are moving.
        if self.last_state == DoorState.Opening:
            #still opening - we could be closing again, but we can't really tell.
            self.set_opening_state()
            
        elif self.last_state == DoorState.Closing:
            #still closing - we could be opening again, but we can't really tell.
            self.set_closing_state()
            
        elif self.last_state == DoorState.Open:
            #we are now closing
            self.set_closing_state()
            
        elif self.last_state == DoorState.Closed:
            #We are now opening
            self.set_opening_state() 
    
    def set_opening_state(self):

        if self.last_state != self.current_state:
            self.reset_state_timers()
            self.opening_state_timer.set_state_start()
            
        self.set_new_state(DoorState.Opening)
        
    def set_closing_state(self):
        if self.last_state != self.current_state:
            self.reset_state_timers()
            self.closing_state_timer.set_state_start()
            
        self.set_new_state(DoorState.Closing)
            
    def set_open_state(self):
        if self.last_state != self.current_state:
            self.reset_state_timers()
            self.open_state_timer.set_state_start()
            
        self.set_new_state(DoorState.Open)
        
    def set_closed_state(self):
        if self.last_state != self.current_state:
            self.reset_state_timers()
            self.closed_state_timer.set_state_start()
        
            
        self.set_new_state(DoorState.Closed)
  
    def is_opening(self):
        return (self.current_state == DoorState.Opening)
    
    def is_closing(self):
        return (self.current_state == DoorState.Closing)
    
    def is_open(self):
        return (self.current_state == DoorState.Open)
    
    def is_closed(self):
        return (self.current_state == DoorState.Closed)
    
    def is_moving(self):
        if self.is_opening() or self.is_closing():
            return True
        return False
        
    def seconds_open(self):
        if self.is_open():
            return self.open_state_timer.seconds_from_timestamp()
        else:
            return 0
    
    def minutes_open(self):
        if self.is_open():
            return self.open_state_timer.minutes_from_timestamp()
        else:
            return 0
        return self.open_door.minutes_from_timestamp()
    
    def seconds_closed(self):
        if self.is_closed():
            return self.closed_state_timer.seconds_from_timestamp()
        else:
            return 0
    
    def minutes_closed(self):
        if self.is_closed():
            return self.closed_state_timer.minutes_from_timestamp()
        else:
            return 0
        
    def seconds_opening(self):
        if self.is_opening():
            return self.opening_state_timer.seconds_from_timestamp()
        else:
            return 0
    
    def minutes_opening(self):
        if self.is_opening():
            return self.opening_state_timer.minutes_from_timestamp()
        else:
            return 0
    
    def seconds_closing(self):
        if self.is_closing():
            return self.closing_state_timer.seconds_from_timestamp()
        else:
            return 0
    
    def minutes_closing(self):
        if self.is_closing():
            return self.closing_state_timer.minutes_from_timestamp()
        else:
            return 0
        
    def state_changed(self):
        return self.current_state != self.last_state
    
    # Evaluates the current state of the door, based on door sensor positions and returns a boolean value, indicating whether or not
    # the state of the door changed since last evaluation. If the state has changed, a message describing the state change is available
    # from the self.state_change_message member.
    def evaluate_door_state(self):
        if self.sensors == 0 or self.sensors is None:
            # no sensors present, which means we can't determine state
            set_unknown_state()
            
        elif self.sensors == 1 and self.closed_sensor is not None :
            #We only have one sensor, so we are either closed or assumed open.
            if self.closed_sensor.is_magnet_aligned():
                self.set_closed_state()
            else:
                self.set_open_state()
                    
        elif self.sensors == 1 and self.open_sensor is not None:
            #We only have one sensor, so we are either open or assumed closed.
            if self.open_sensor.is_magnet_aligned():
                self.set_open_state()
            else:
                self.set_closed_state()
            
        elif self.sensors == 2 and self.closed_sensor is not None and self.open_sensor is not None:
            # We have two sensors, we should be able to determine if we are open, closed, in an opening or closing state.
            if self.closed_sensor.is_magnet_aligned() and self.open_sensor.is_magnet_aligned():
                message = "This should be physically impossible. The door is both open and closed at the same time...Call Einstein, we have discovered new physics."
                #raise ValueError(message)
            
            elif self.closed_sensor.is_magnet_aligned():
                self.set_closed_state()
                
            elif self.open_sensor.is_magnet_aligned():
                self.set_open_state()
                
            else:
                # The door is somewhere between fully opened and fully closed.
                self.set_moving_state()
        else:
            message = "Something is wrong in the sensor settings for this Door instance."
            raise ValueError(message)
        
        if(self.state_changed()):
            self.state_change_message = "Door state changed from {} to {}".format(DoorState.state_string(self.last_state), DoorState.state_string(self.current_state))
            return True
        else:
            return False            
    
    #Sends a signal to the relay switch to open the garage door, if the current state is closed, and returns True and DoorState.Opening.
    #If the garage door is not in a closed state, False and the current DoorState is returned. (e.g. DoorState.Closed)
    def open_the_door(self):
        #print('opening door')
        self.evaluate_door_state()
        if self.is_closed():
            self.relay_switch.toggle(1, 1)
            self.set_opening_state()
            self.evaluate_door_state()
            return True, self.current_state
        else:
            return False, self.current_state
    
    #Sends a signal to the relay switch to close the garage door, if the current state is not closed, and returns True and DoorState.Closing.
    #If the garage door is already in a closed state, False and DoorState.Closed is returned.
    def close_the_door(self):
        #print('closing door')
        self.evaluate_door_state()
        if not self.is_closed():
            self.relay_switch.toggle(1, 1)
            self.set_closing_state()
            self.evaluate_door_state()
            return True, self.current_state
        else:
            return False, self.current_state            
        
    # This method creates a door instance with a relay switch at the given pin, none, one or two door sensors initialized
    # to the given pins. If no pin values are given, pin 16 is used for the closed door sensor
    # and pin 18 for the open door sensor. If you want to create a Door instance with 1 or no sensors
    # submit a negative value for the pin you are not using.
    @classmethod
    def create_instance(cls, relay_switch_pin, closed_door_sensor_pin, open_door_sensor_pin, warn_after_open_minutes, warn_after_minutes_in_moving_state):
        relay = DoorRelay(relay_switch_pin)
        if open_door_sensor_pin > 0:
            open_sensor = DoorSensor(open_door_sensor_pin)
        
        if closed_door_sensor_pin > 0:
            closed_sensor = DoorSensor(closed_door_sensor_pin) 
        
        instance = cls(relay, closed_sensor, open_sensor, warn_after_open_minutes, warn_after_minutes_in_moving_state)
        instance.evaluate_door_state()
        return instance
    
    # This method creates a door instance based on the settings in the doorSettings file.
    @classmethod
    def create_instance_from_settings(cls):
        settings = AppSettings("doorSettings")
        try:
            settings_values = settings.get_values_for_keys(["relay pin", "closed door sensor pin", "open door sensor pin", "warn when open for minutes", "warn when moving for secs"])

            # Mandatory setting: relay_pin
            relay_pin = int(settings_values[0]) if len(settings_values) > 0 and settings_values[0].isdigit() else None
            if relay_pin is None:
                raise ValueError("Relay pin configuration is missing or invalid.")

            # Optional settings with defaults
            closed_pin = int(settings_values[1]) if len(settings_values) > 1 and settings_values[1].isdigit() else default_closed_pin_value
            open_pin = int(settings_values[2]) if len(settings_values) > 2 and settings_values[2].isdigit() else default_open_pin_value
            open_min_warn = int(settings_values[3]) if len(settings_values) > 3 and settings_values[3].isdigit() else default_open_min_warn
            move_sec_warn = int(settings_values[4]) if len(settings_values) > 4 and settings_values[4].isdigit() else default_move_sec_warn
            
        except ValueError as e:
            print(f"Error in settings configuration: {e}")
            raise 

        return cls.create_instance(relay_pin, closed_pin, open_pin, open_min_warn, move_sec_warn)
    
