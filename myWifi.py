import network
import binascii
import time
import socket
from appSettings import AppSettings

class MyWifi:
    
    #create MyWifi instance with the given ssid and password.
    #if auto_connect is set to True the constructor will attempt to connect after instantiation. 
    def __init__(self, ssid, password, auto_connect = True, troubleshooting = False):
        self.ssid = ssid
        self.pwd = password
        self.ip = '0.0.0.0'
        self.wlan = None
        if auto_connect:
            self.connect(troubleshooting)
    
    # checks if the instance is connected to wifi
    def is_connected(self):
        if self.wlan is None:
            return False
        else:
            return self.wlan.isconnected()
        
    #Connect to wifi 
    def connect(self, troubleshooting = False, max_tries = 10):

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        networks = wlan.scan()
        ssid_found = False
    
        # Find the network with matching SSID (case-insensitive)
        for ssid, *_ in networks:
            if ssid.decode().lower() == self.ssid.lower():
                self.ssid = ssid.decode()
                wlan.connect(self.ssid, self.pwd)
                ssid_found = True
                break
         
        if not ssid_found:
            raise ValueError("SSID not found")
        
        i = 0
        while not wlan.isconnected() and i < max_tries:
            if i == 0:
                print('Waiting for connection')
            print('.', end='') 
            i += 1
            time.sleep(1)
        
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f'Connected on {ip}')
            self.ip = ip
            self.wlan = wlan
            
        elif troubleshooting:
            config = wlan.ifconfig()
            print("Network configuration:", config)
            self.print_wlan_status()
        else:
            self.print_wlan_status()
            raise RuntimeError('Network connection failed.')
        
    def print_wlan_status(self):
        if self.wlan is not None:
            print("Wlan is active: ", self.wlan.active())

            status = self.wlan.status()
            if status == network.STAT_IDLE:
                print("WLAN status: IDLE (no connection and no activity)")
            elif status == network.STAT_CONNECTING:
                print("WLAN status: CONNECTING (connecting in progress)")
            elif status == network.STAT_WRONG_PASSWORD:
                print("WLAN status: WRONG PASSWORD (failed due to incorrect password)")
            elif status == network.STAT_NO_AP_FOUND:
                print("WLAN status: NO AP FOUND (failed because no access point replied)")
            elif status == network.STAT_CONNECT_FAIL:
                print("WLAN status: CONNECT FAIL (failed due to other problems)")
            elif status == network.STAT_GOT_IP:
                print("WLAN status: GOT IP (connection successful)")
        else:
            print("WLAN not initialized")
    
    #opens a socket on given ip and port
    def open_socket(self, ip = None, port = 80):
        
        if self.is_connected():
            # Open a socket for the webserver to listen to
            if ip is None:
                ip = self.ip
                
            address = (ip, port)
            print(address)
            connection = socket.socket()
            connection.bind(address)
            connection.listen(1)
            print(f'Listening on port {port}')
            return connection
        else:
            print ("Not connectd to wifi")

    @classmethod
    def wlan_scan(cls):
        # Scan WiFi network and return the list of available access points.
        # Each list entry is a tuple with the following items:
        # (ssid, bssid, primary_chan, rssi (signal Strength), auth_mode, [ hidden])

        wlan = network.WLAN(network.STA_IF)
        _ = wlan.active(True)
        # names of authentication modes - based on esp32 docs - other ports do differ in values
        AUTH_MODES = {
            0: "Open",
            1: "WEP",
            2: "WPA-PSK",
            3: "WPA2-PSK",
            4: "WPA/WPA2-PSK",
            5: "WPA2-EAS",
            6: "WPA3-PSK",
            7: "WPA2/WPA3-PSK",
        }

        wlan.status()


        def _authmode(mode: int):
            try:
                return AUTH_MODES[mode]
            except KeyError:
                # handle unknown modes
                return "mode-{}".format(mode)


        def _hidden(net: tuple):
            return net[5] if len(net) > 5 else "-"


        _networks = wlan.scan()
        # sort on signal strength
        _networks = sorted(_networks, key=lambda x: x[3], reverse=True)
        # define columns and formatting
        _f = "{0:<32} {1:>12} {2:>8} {3:>6} {4:<13} {5:>8}"
        print(_f.format("SSID", "MAC address", "Channel", "Signal", "Authmode", "Hidden"))
        for _net in _networks:
            print(_f.format(_net[0], binascii.hexlify(_net[1]), _net[2], _net[3], _authmode(_net[4]), _hidden(_net)))

        del _f, _networks



    @classmethod
    def create_instance_from_settings(cls, auto_connect = True, troubleshooting = False):
        settings = AppSettings("netCred")
        try:
            ssid, password = settings.get_values_for_keys(["ssid", "password"])
            print(f'<{ssid}><{password}>')
            
        except ValueError as e:
            print(f"Error in settings configuration: {e}")
            raise 

        return cls(ssid, password, auto_connect, troubleshooting)
    

#tests
#MyWifi.wlan_scan()

#ssid=""
#pwd="!"
#wifi = MyWifi(ssid, pwd, False)
#wifi.connect()
#wifi.print_wlan_status()
#wifi.open_socket('0.0.0.0', 5001)

