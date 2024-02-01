from appSettings import AppSettings
import myNetworkLib

def connect_wifi():
    try:
        
        settings = AppSettings("netCred")
        ssid, pwd = settings.get_values_for_keys(["ssid", "password"])
        ipAddr = myNetworkLib.connect_wifi(ssid, pwd, False)

    except Exception as e:
        print("Error:", e)
