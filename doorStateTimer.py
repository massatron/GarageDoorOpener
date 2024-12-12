import time
class DoorStateTimer:
    
    # time_unit can be "m" for minutes or "s" for seconds. Anything else will be treated as mintues.
    def __init__(self, doorstate):
        self.doorstate = doorstate
        self.set_state_start()
        
    def reset(self):
        self.start_time = None

    def minutes_from_timestamp(self):
        if self.start_time is None:
            return 0
        difference_minutes =self.seconds_from_timestamp() / 60
        return int(difference_minutes)
    
    def seconds_from_timestamp(self):
        if self.start_time is None:
            return 0
        now_stamp = time.mktime(time.localtime())
        difference_secs = (now_stamp - self.start_time)
        return int(difference_secs)
    
    def set_state_start(self):
        self.start_time = time.mktime(time.localtime())

