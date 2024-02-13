from machine import Pin, I2C
import machine
import ujson
from picozero import pico_led
from door import *

class DoorCommandListener:
    # creates a listener on a port for a given MyWifi connection and Door
    # if wifi is not connected a ValueError is thrown.
    def __init__(self, door_to_control, myWifi, port = 5002, start_listening = True):
        
        self.door = door_to_control
        
        if myWifi.is_connected():
            self.connection = myWifi.open_socket(myWifi.ip, port)
            self.is_listening = False
        else:
            raise ValueError("Wifi is not connected.")
    
        if start_listening:
            self.start()
    
    # sends the current door state back to the client using given connection.
    def return_door_state(self, connection = None, print_to_console = False):
        # evaluate current state
        door_state_changed = self.door.evaluate_door_state()
        current_door_state = self.door.get_current_state_string()
        
        if print_to_console:
            print(f'Current door state: {current_door_state}')
            print(f'Listening for command.')
        
        if connection is not None:
            # send state back to client
            connection.send(current_door_state.encode())
    
    # Starts the listener
    def start(self, print_to_console = False):
        
        self.return_door_state(None, print_to_console)
        self.is_listening = True
                    
        while self.is_listening:
            
            #wait for incoming connection
            conn, addr = self.connection.accept()
            
            if print_to_console:
                print(f'Connecting from: {addr}')
                
            # Receive a command from the client
            data = conn.recv(1024).decode()
            command = ujson.loads(data)
            
            if print_to_console:
                print(f'Command: {command}')
            
            # check if we have a valid Door command

            if command == 'open':
                self.door.open_the_door()
            elif command == 'close':
                self.door.close_the_door()
            elif command == 'stop':
                self.is_listening = False
            elif command == 'reboot':
                machine.reset()
            elif command == 'sleep':
                machine.deepsleep()
            elif command == 'status':
                self.return_door_state(conn, print_to_console)  
            elif print_to_console:
                print('Invalid value for "gpio":', gpio_value)
            else:
                print('Invalid command received."')
            
            print(f'Current door state is: {DoorState.state_string(self.door.current_state)}')
            conn.close()
            




