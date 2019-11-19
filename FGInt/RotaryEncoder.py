# File: encoder.py
# Scott M Baker, http://www.smbaker.com/

# Raspberry Pi Driver for the Sparkfun RGB Encoder (COM-10982 or COM-10984)

# Acknowledgements:
#    py-gaugette by Guy Carpenter, https://github.com/guyc/py-gaugette

import math
import threading
import time

class RotaryEncoder:
    # Just the encoder, no switch, no LEDs

    def __init__(self, device, encodername, port, in1, in2, swin, initvalue, minvalue, maxvalue, increment, debug=0):
        self.debug = debug
        self.device = device
        self.encodername = encodername
        self.port = port
        self.a_pin = int(in1)
        self.b_pin = int(in2)
        self.sw_pin = int(swin)
        self.value = initvalue
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.increment = increment
        self.last_delta = 0
        self.r_seq = self.rotation_sequence()
        self.steps_per_cycle = 2    # 4 steps between detents
        self.remainder = 0

    def rotation_sequence(self):
        a_state = self.device.getPin(self.port, self.a_pin)
        b_state = self.device.getPin(self.port, self.b_pin)
        r_seq = (a_state ^ b_state) | b_state << 1
        return r_seq

    # Returns offset values of -2,-1,0,1,2
    def get_delta(self):
        delta = 0
        r_seq = self.rotation_sequence()
        if r_seq != self.r_seq:
            delta = (r_seq - self.r_seq) % 4
            if delta==3:
                delta = -1
            elif delta==2:
                delta = int(math.copysign(delta, self.last_delta))  # same direction as previous, 2 steps

            self.last_delta = delta
            self.r_seq = r_seq

        return delta

    def get_cycles(self):
        self.remainder += self.get_delta()
        cycles = self.remainder // self.steps_per_cycle
        self.remainder %= self.steps_per_cycle # remainder always remains positive
        return cycles

    def get_switchstate(self):
        return self.device.getPin(self.port, self.sw_pin)

    def getEncoderValue(self):
        return self.value

    def setEncoderValue(self, value):
        self.value = value

class EncoderWorker(threading.Thread):
    def __init__(self, encoder):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.stopping = False
        self.encoder = encoder
        self.daemon = True
        self.delta = 0
        self.delay = 0.001
        self.lastSwitchState = False
        self.upEvent = False
        self.downEvent = False
        #print("class Encoder : {}".format(self.encoder.__class__.__name__))

    def run(self):
        #self.lastSwitchState = self.encoder.get_switchstate()
        while not self.stopping:
            delta = self.encoder.get_cycles()
            with self.lock:
                self.delta += delta
                '''
                self.switchstate = self.encoder.get_switchstate()
                if (not self.lastSwitchState) and (self.switchstate):
                    self.upEvent = True
                if (self.lastSwitchState) and (not self.switchstate):
                    self.downEvent = True
                self.lastSwitchState = self.switchstate
                '''
            time.sleep(self.delay)

    # get_delta, get_upEvent, and get_downEvent return events that occurred on
    # the encoder. As a side effect, the corresponding event will be reset.

    def get_delta(self):
        with self.lock:
            delta = self.delta
            self.delta = 0
        return delta

    def get_upEvent(self):
        with self.lock:
            delta = self.upEvent
            self.upEvent = False
        return delta

    def get_downEvent(self):
        with self.lock:
            delta = self.downEvent
            self.downEvent = False
        return delta

    def getValue(self):
        return self.encoder.getEncoderValue()

    def setValue(self, value):
        self.encoder.setEncoderValue(value)

    def getMinValue(self):
        return self.encoder.minvalue

    def getMaxValue(self):
        return self.encoder.maxvalue

    def getIncrement(self):
        return self.encoder.increment
