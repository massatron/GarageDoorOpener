import threading
from myWifi import MyWifi
from door import *
from doorMonitor import DoorMonitor
from doorCommandListener import DoorCommandListener

def listen_for_command(door):
    wifi =  MyWifi.create_instance_from_settings()
    print(f"Door state before starting listener: {DoorState.state_string(door.current_state)}")
    doorCmdListener = DoorCommandListener(door, wifi, port = 5002, start_listening = True)
    #doorCmdListener.start(True)

def main():
    
    
    
    door = Door.create_instance_from_settings()
    
    # Initialize and start DoorMonitor
    door_monitor = DoorMonitor.create_instance(door)
    #monitor_thread = threading.Thread(target=door_monitor.start)
    #monitor_thread.start()


    listen_for_command(door)  # Your logic to listen for commands


if __name__ == "__main__":
    main()
    
