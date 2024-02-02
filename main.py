import threading
from connectWifi import connect_wifi
from door import Door
from doorMonitor import DoorMonitor

def listen_for_command():
    import time
    time.sleep(5)
    return "Open Door"

def main():
    
    connect_wifi()
    
    door = Door.create_instance_from_settings()
    
    # Initialize and start DoorMonitor
    door_monitor = DoorMonitor.create_instance(door)
    monitor_thread = threading.Thread(target=door_monitor.start)
    monitor_thread.start()

    while True:
        command = listen_for_command()  # Your logic to listen for commands
        if command == "Open Door":
            door.open_door()
        elif command == "Close Door":
            door.close_door()


if __name__ == "__main__":
    main()
    
