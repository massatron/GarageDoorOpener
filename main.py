from connectWifi import connect_wifi
from doorMonitor import *

try:
    #connect_wifi()
    DoorMonitor.create_instance(start = True)
    
except Exception as e:
    print("Error:", e)
