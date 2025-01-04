import uasyncio as asyncio
import ujson

class DoorCommandListener:
    def __init__(self, door_to_control, myWifi, listen_port=5002, print_to_console=True):
        self.door = door_to_control
        self.listen_port = listen_port
        self.print_to_console = print_to_console

        if not myWifi.is_connected():
            raise ValueError("Wifi is not connected.")

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        if self.print_to_console:
            print(f'Connection from: {addr}')

        try:
            data = await reader.read(1024)
            command = ujson.loads(data.decode())

            if self.print_to_console:
                print(f'Data received: {data.decode()}')
                print(f'Command: {command}')

            if 'gpio' in command:
                gpio_value = command['gpio']
                if gpio_value == 'open':
                    self.door.open_the_door()
                elif gpio_value == 'close':
                    self.door.close_the_door()
                elif gpio_value == 'stop':
                    writer.write("Server stopping...".encode())
                    await writer.drain()
                    self.is_listening = False
                elif gpio_value == 'status':
                    await self.return_door_state(writer)
                elif gpio_value == "minutes_in_state":
                    await self.return_minutes_in_state(writer)
                elif gpio_value == "seconds_in_state":
                    await self.return_seconds_in_state(writer)
                elif gpio_value == "validate_connection":
                    writer.write(f"{addr[0]}:{addr[1]}".encode())
                    await writer.drain()
                elif self.print_to_console:
                    print('Invalid value for "gpio":', gpio_value)
            else:
                print('Error: Missing keys "gpio"')
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            await writer.drain()
            await writer.wait_closed()
        
    async def return_door_state(self, writer):
        # Evaluate the door state here
        door_state_changed = self.door.evaluate_door_state()
        current_door_state = self.door.get_current_state_string()

        if self.print_to_console:
            print(f"Current door state: {current_door_state}")

        writer.write(current_door_state.encode())
        await writer.drain()

    async def return_minutes_in_state(self, writer):
        minutes_in_state = max(
            self.door.minutes_open(),
            self.door.minutes_closed(),
            self.door.minutes_opening(),
            self.door.minutes_closing(),
        )
        writer.write(str(minutes_in_state).encode())
        await writer.drain()

    async def return_seconds_in_state(self, writer):
        seconds_in_state = max(
            self.door.seconds_open(),
            self.door.seconds_closed(),
            self.door.seconds_opening(),
            self.door.seconds_closing(),
        )
        writer.write(str(seconds_in_state).encode())
        await writer.drain()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, "0.0.0.0", self.listen_port)
        if self.print_to_console:
            print(f"Server listening on port {self.listen_port}")
    
        # Manually run the server's event loop
        while True:
            await asyncio.sleep(1)  # Keeps the event loop alive
            
