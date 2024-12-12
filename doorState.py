class DoorState:
    Open = 1
    Closed = 2
    Unknown = 3
    Opening = 4
    Closing = 5
    
    def state_string(state):
        if state == 1:
            return "Open"
        if state == 2:
            return "Closed"
        if state == 3:
            return "Unknown"
        if state == 4:
            return "Opening"
        if state == 5:
            return "Closing"
        
        raise ValueError("DoorState value: ", state, " is invalid")