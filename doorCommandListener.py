from machine import Pin, I2C
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
            
    # Starts the listener
    def start(self, print_to_console = False):
        
        self.is_listening = True
        
        while self.is_listening:
            
            if print_to_console:
                print(f'Listening.')
            
            #wait for incoming connection
            conn, addr = self.connection.accept()
            
            if print_to_console:
                print(f'Connecting from: {addr}')
                
            # Receive a command from the client
            data = conn.recv(1024).decode()
            command = ujson.loads(data)
            
            if print_to_console:
                print(f'Data received: {data}')
                print(f'Command: {command}')
            
            # check if we have a valid Door command
            if 'gpio' in command:
                gpio_value = command['gpio']
                if gpio_value == 'open':
                    self.door.open_the_door()
                elif gpio_value == 'close':
                    self.door.close_the_door()
                elif gpio.value == 'stop':
                    self.is_listening = False
                elif gpio.value == 'status':
                    response = f'Current door state is: {self.door.current_state}'
                    conn.send(response.encode())
                elif print_to_console:
                    print('Invalid value for "gpio":', gpio_value)
            else:
                print('Error: Missing keys "gpio" and "info"')
            
            print(f'Current door state is: {DoorState.state_string(self.door.current_state)}')
            conn.close()
            




