from myWifi import MyWifi
from door import *
from doorMonitor import *
from doorCommandListener import *
import time

def main():
    wifi = MyWifi.create_instance_from_settings()
    door = Door.create_instance_from_settings()
    print(f"Door state before starting listener: {DoorState.state_string(door.current_state)}")
    doorCmdListener = DoorCommandListener(door, wifi, start_listening=True)

main()