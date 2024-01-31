import socket
import network
import binascii
from time import sleep

def wlan_scan():
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

def print_wlan_status(wlan):
    print("Wlan is active: ", wlan.active())
    
    status = wlan.status()
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
        
def connect_wifi(ssid, password, troubleshooting = False):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    maxTries = 15
    i = 0
    while not wlan.isconnected() and i < maxTries:
        print('Waiting for connection...')
        
        if(troubleshooting):
            print_wlan_status(wlan)
            
        i += 1
        sleep(1)
    
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f'Connected on {ip}')
        return ip
    else:
        config = wlan.ifconfig()
        print("Network configuration:", config)
        raise RuntimeError('Network connection failed.')

def openSocket(ip = '0.0.0.0', port = 80):
    # Open a socket for the webserver to listen to
    address = (ip, port)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(f'Listening on port {port}')
    return connection
