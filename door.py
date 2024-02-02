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
            

class DoorState:
    Open = 1
    Closed = 2
    Unknown = 3
    Opening = 4
    Closing = 5
    
    def status_string(status):
        if status == 1:
            return "Open"
        if status == 2:
            return "Closed"
        if status == 3:
            return "Unknown"
        if status == 4:
            return "Opening"
        if status == 5:
            return "Closing"
        
        raise ValueError("DoorState value: ", status, " is invalid")
    
class DoorSensor:
    def __init__(self, gpioPin):
        self.gpioPin = gpioPin
        GPIO.setup(gpioPin, GPIO.IN, GPIO.PUD_UP)
    
    def is_magnet_aligned(self):  
        return (GPIO.input(self.gpioPin) == GPIO.HIGH)

class DoorMessage:
    
    # time_unit can be "m" for minutes or "s" for seconds. Anything else will be treated as mintues.
    def __init__(self, message, send_after_time_units = 15, time_unit = "m", message_sent_init = False, timestamp = None):
        self.sent = False
        self.send_after_time_units = send_after_time_units
        self.message = message
        self.timestamp = timestamp
        self.time_unit = time_unit
    
    def clear(self):
        self.timestamp = None
        self.sent = None
        
    def set(self):
        self.reset()
        
    def reset(self):
        self.timestamp = time.mktime(time.localtime())
        self.sent = False
        
    def send_message(self):
        if self.time_unit == "s" and self.seconds_from_timestamp() >= self.send_after_time_units and self.sent is not None and not self.sent:
            print(self.message)
            self.sent = True            
        elif self.minutes_from_timestamp() >= self.send_after_time_units and self.sent is not None and not self.sent:
            print(self.message)
            self.sent = True
    
    def minutes_from_timestamp(self):
        if self.timestamp == None:
            return 0
        difference_minutes =self.seconds_from_timestamp() / 60
        return difference_minutes
    
    def seconds_from_timestamp(self):
        if self.timestamp == None:
            return 0
        now_stamp = time.mktime(time.localtime())
        difference_secs = (now_stamp - self.timestamp)
        return difference_secs    

class Door:
    
    def __init__(self, relay_switch, door_sensor_closed=None, door_sensor_open=None, warn_when_open_minutes = 15, warn_when_moving_seconds = 15):
        self.relay_switch = relay_switch
        self.current_state = DoorState.Unknown
        self.last_state = DoorState.Unknown
        #self.open_door_message_sent = True
        #self.warning_minutes = warn_when_open_minutes
        message = "Your Garage Door has been open for {} minutes".format(warn_when_open_minutes)       
        self.open_door = DoorMessage(message, warn_when_open_minutes, "m", True)
            
        message = "Your Garage Door has been in a not open and not closed state for {} seconds. Is it stuck?".format(warn_when_moving_seconds)
        self.moving_door = DoorMessage(message, warn_when_moving_seconds, "s", True)
        
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
    
    # sets current state to the supplied state and
    # sets the last_state to the current state
    def set_new_state(self, new_state):
        self.last_state = self.current_state
        self.current_state = new_state
    
    def set_unknown_state(self):
        self.set_new_state(DoorState.Unknown)
        self.open_door.timestamp = None
        self.open_door.sent = None
    
    #probably either opening or closing, but could be stopped in between somewhere
    def set_moving_state(self):
        #track how long the door has been in a non-open/non-closed state
        if self.moving_door.timestamp == None:
            self.moving_door.reset()
            
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
        
        self.open_door.send_message()
        self.moving_door.send_message()
    
    def set_opening_state(self):
        if self.open_door.timestamp == None:
            self.open_door.set()
        self.set_new_state(DoorState.Opening)
            
    def set_closing_state(self):
        self.set_new_state(DoorState.Closing)
            
    def set_open_state(self):
        if self.open_door.timestamp == None:
            self.open_door.reset()
        else:
            self.open_door.send_message()
            
        self.set_new_state(DoorState.Open)
        self.moving_door.clear()
        
    def set_closed_state(self):
        self.set_new_state(DoorState.Closed)
        self.open_door.clear()
        self.moving_door.clear()     
    
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
        if self.is_closed():
            return 0
        return self.open_door.seconds_from_timestamp()
    
    def seconds_moving(self):
        if self.is_moving():
            return self.moving_door.seconds_from_timestamp()
        return 0
    
    def minutes_moving(self):
        if self.is_moving():
            return self.moving_door.minutes_from_timestamp()
        return 0
    
    def minutes_open(self):
        if self.is_closed() or self.is_closing():
            return 0
        return self.open_door.minutes_from_timestamp()
    
    def state_changed(self):
        return self.current_state != self.last_state
    
    # Evaluates the current state of the door, based on door sensor positions and returns a boolean value, indicating whether or not
    # the state of the door changed since last evaluation. If the state has changed, a message describing the state change is available
    # from the self.state_change_message member.
    def evaluate_door_state(self):
        if self.sensors == 0 or self.sensors == None:
            # no sensors present, which means we can't determine state
            set_unknown_state()
            
        elif self.sensors == 1 and self.closed_sensor != None :
            #We only have one sensor, so we either closed or assumed open.
            if self.closed_sensor.is_magnet_aligned():
                self.set_closed_state()
            else:
                self.set_open_state()
                    
        elif self.sensors == 1 and self.open_sensor != None:
            #We only have one sensor, so we either open or assumed closed.
            if self.open_sensor.is_magnet_aligned():
                self.set_open_state()
            else:
                self.set_closed_state()
            
        elif self.sensors == 2 and self.closed_sensor != None and self.open_sensor != None:
            # We have two sensors, we should be able to determine if we are open, closed, in an opening or closing state.
            if self.closed_sensor.is_magnet_aligned() and self.open_sensor.is_magnet_aligned():
                message = "This should be physically impossible. The door is both open and closed at the same time...Call Einstein, we have discovered new physics."
                raise ValueError(message)
            
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
            self.state_change_message = "Door state changed from {} to {}".format(DoorState.status_string(self.last_state), DoorState.status_string(self.current_state))
            return True
        else:
            return False            
    
    #Sends a signal to the relay switch to open the garage door, if the current status is closed, and returns True and DoorState.Opening.
    #If the garage door is not in a closed state, False and the current DoorState is returned. (e.g. DoorState.Closed)
    def open_door(self):
        if self.is_closed():
            self.relay_switch.toggle(1, 1)
            self.set_new_state(DoorState.Opening)
            return True, self.current_state
        else:
            return False, self.current_state
    
    #Sends a signal to the relay switch to close the garage door, if the current status is not closed, and returns True and DoorState.Closing.
    #If the garage door is already in a closed state, False and DoorState.Closed is returned.
    def close_door(self):
        if not self.is_closed():
            self.relay_switch.toggle(1, 1)
            self.set_new_state(DoorState.Closing)
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
        
        return cls(relay, closed_sensor, open_sensor, warn_after_open_minutes, warn_after_minutes_in_moving_state)
   
