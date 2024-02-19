from machine import Pin, I2C
import machine
from door import Door

class DoorCommandListener:
    # creates a listener on a port for a given MyWifi connection and Door
    # if wifi is not connected a ValueError is thrown.
    def __init__(self, door_to_control, myWifi, port = 5002, start_listening = True, print_to_console = False):
        
        self.door = door_to_control
        self.print_to_console = print_to_console
        self.myWifi = myWifi
        
        if myWifi.is_connected():
            self.connection = myWifi.open_socket(myWifi.ip, port)
            self.is_listening = False
        else:
            raise ValueError("Wifi is not connected.")
    
        if start_listening:
            self.start_server()
    
    # sends the current door state back to the client using given connection.
    async def return_door_state(self, writer):
        # evaluate current state
        door_state_changed = self.door.evaluate_door_state()
        current_door_state = self.door.get_current_state_string()
        
        if self.print_to_console:
            print(f'Current door state: {current_door_state}')
            print(f'Listening for command.')
        
        writer.write(current_door_state.encode())
        await writer.drain()  # Ensure response is sent
    
    # sends a given mesage back to client
    async def return_message (self, writer, message):
        if self.print_to_console:
            print(message)
        
        writer.write(message.encode())
        await writer.drain()  # Ensure response is sent
            

    async def handle_client(self, reader, writer):
        import ujson

        while self.is_listening:
            
            data = await reader.read(1024)  # Non-blocking read
            
            if not data:
                writer.close()
                await writer.wait_closed()
                break  # If no data, close the connection
            
            try:
                message = ujson.loads(data.decode().strip())
                command = message['command']
            except:
                command = "invalid"
                
            try:
                # check if we have a valid Door command
                print(f"Received command: {command}")
                
                if command == 'open':
                    self.door.open_the_door()
                    await self.return_message(writer, "Opening door")
                elif command == 'close':
                    self.door.close_the_door()
                    await self.return_message(writer, "Closing door")
                elif command == 'stop':
                    await self.return_message(writer, "Stopping listener.")
                    self.is_listening = False
                elif command == 'reboot':
                    await self.return_message(writer, "Rebooting server.")
                    machine.reset()
                elif command == 'sleep':
                    await self.return_message(writer, "Putting server to sleep")
                    machine.deepsleep()
                elif command == 'status':
                    await self.return_door_state(writer)  
                else:
                    await self.return_message(writer, "Invalid command received.")
            except:
                writer.close()
                await writer.wait_closed()
                break  # close the connection

        writer.close()
        await writer.wait_closed()

    async def start_server(self):
        import uasyncio as asyncio
        self.is_listening = True
        
        _, local_port = self.connection.getsockname()
        server = await asyncio.start_server(self.handle_client, self.myWifi.ip, local_port)
        
        async with server:
            await server.serve_forever()
            





