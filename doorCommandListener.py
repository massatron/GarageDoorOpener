import socket
import ujson
from myWifi import MyWifi
from door import Door
from doorMonitor import DoorState
from picozero import pico_led

class DoorCommandListener:
    def __init__(self, door_to_control, myWifi, listen_port=5002, start_listening=False, print_to_console=True):
        self.door = door_to_control

        if myWifi.is_connected():
            self.connection = myWifi.open_socket(myWifi.ip, listen_port, True)
            self.is_listening = False
        else:
            raise ValueError("Wifi is not connected.")

        if start_listening:
            self.start(print_to_console)

    def return_door_state(self, conn, print_to_console=True):
        door_state_changed = self.door.evaluate_door_state()
        current_door_state = self.door.get_current_state_string()

        if print_to_console:
            print(f'Current door state: {current_door_state}')

        if conn is not None:
            conn.send(current_door_state.encode())
    
    def return_minutes_in_state(self, conn, print_to_console=True):
        # all but one should be 0
        opn = self.door.minutes_open()
        closed = self.door.minutes_closed()
        opening = self.door.minutes_opening()
        closing = self.door.minutes_closing()
        
        minutes_in_state = max(opn, closed, opening, closing)
    
        if print_to_console:
            print(f'Minutes in state {self.door.get_current_state_string()}: {minutes_in_state}')

        if conn is not None:
            conn.send(str(minutes_in_state).encode())

    def return_seconds_in_state(self, conn, print_to_console=True):
        # all but one should be 0
        opn = self.door.seconds_open()
        opening = self.door.seconds_opening()
        closed = self.door.seconds_closed()
        closing = self.door.seconds_closing()
        
        seconds = max(opn, closed, opening, closing)
    
        if print_to_console:
            print(f'Seconds in state {self.door.get_current_state_string()}: {seconds}')

        if conn is not None:
            conn.send(str(seconds).encode())
            
    def return_connection_info(self, conn, address, print_to_console=True):
        if print_to_console:
            print(f"Returning connection information {address[0]}:{address[1]}")

        if conn is not None:
            conn.send(str(f"{address[0]}:{address[1]}").encode())
            

    def start(self, print_to_console=False):
        self.return_door_state(None, print_to_console)
        self.is_listening = True

        while self.is_listening:
            conn, addr = self.connection.accept()

            if print_to_console:
                print(f'Connecting from: {addr}')
            try:
                data = conn.recv(1024).decode()
                command = ujson.loads(data)

                if print_to_console:
                    print(f'Data received: {data}')
                    print(f'Command: {command}')

                if 'gpio' in command:
                    gpio_value = command['gpio']
                    if gpio_value == 'open':
                        self.door.open_the_door()
                    elif gpio_value == 'close':
                        self.door.close_the_door()
                    elif gpio_value == 'stop':
                        self.is_listening = False
                    elif gpio_value == 'status':
                        self.return_door_state(conn, print_to_console)
                    elif gpio_value == "minutes_in_state":
                        self.return_minutes_in_state(conn, print_to_console)
                    elif gpio_value == "seconds_in_state":
                        self.return_seconds_in_state(conn, print_to_console)
                    elif gpio_value == "validate_connection":
                        self.return_connection_info(conn, addr, print_to_console)
                    elif print_to_console:
                        print('Invalid value for "gpio":', gpio_value)
                else:
                    print('Error: Missing keys "gpio"')
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                if conn:
                    conn.close()
            
            print(f'Current door state is: {DoorState.state_string(self.door.current_state)}')
