from machine import Pin

class LED():
    def __init__(self, pin):
        self.pin = pin
        self.led = Pin(pin, Pin.OUT)
        self.off()
    def on(self):
        self.led.on()
    def off(self):
        self.led.off()       

class Button():
    btnList = {}
    def __init__(self, pin):
        self.pin = pin
        self.btn = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.state = self.btn.value()
        self.when_pressed  = None
        self.when_released = None
        btnList[pin] = self
    def value(self):
        return self.btn.value()
    def pressed(self):
        if self.when_pressed != None:
            self.when_pressed()
    def released(self):
        if self.when_released != None:
            self.when_released()
    def check(self):
        if self.btn.value() != self.state:
            self.state = self.state ^ 1
            if self.state == 0:
                self.released()
            else:
                self.pressed()
    def pause(listButtons=False):
        if listButtons:
            print(Button.btnList)
        while len(Button.btnList) > 0:
            for btn in Button.btnList:
                Button.btnList[btn].check()

pause = Button.pause()