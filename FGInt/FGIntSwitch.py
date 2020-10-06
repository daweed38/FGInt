#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import operator
import time
import datetime

# Standard Modules Import

###################################
# FarmerSoft FlightGear Interface
###################################
# DISPLAY Class (Affichage)
# FarmerSoft © 2015
# By Daweed
###################################

class Switch:
    """
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    def __init__(self, device, name, port, pin, values, valuestype, invert, node, debug=0):
        self.debug = debug
        self.device = device
        self.name = name
        self.port = str(port)
        self.pin = int(pin)
        self.values = values.split(',')
        self.valuestype = valuestype
        self.invert = int(invert)
        self.node = node
        self.swstate = self.values[0] 
        if self.debug == 5:
            print("######################################################################")
            print("# Creation du Switch {} sur le port {}".format(self.name, self.port))
            print("# du device {} de class {}".format(self.device.devicename, self.device.__class__.__name__))
            print("# Etat du Switch : {}".format(self.getSwitchState()))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 5:
            print("######################################################################")
            print("# Destruction du Switch {}".format(self.name))
            print("######################################################################")
            print("\r")
    
    ###############
    # Methodes
    ###############
    def getValueType(self):
        return self.valuestype

    def getNode(self):
        return self.node

    def getTypedData(self, data):
        if self.valuestype == 'string':
            return str(data)
        elif self.valuestype == 'int':
            return int(data)
        elif self.valuestype == 'bool':
            return bool(data)
        else:
            return int(data)

    def getSwitchState(self):
        self.swpinstate = self.device.getPin(self.port, self.pin)
        if self.swpinstate == 1:
            if self.invert == 1:
                self.swstate = self.values[0]
            else:
                self.swstate = self.values[1]
        else:
            if self.invert == 1:
                self.swstate = self.values[1]
            else:
                self.swstate = self.values[0]
        return self.swstate


class DoubleSwitch:
    """
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    def __init__(self, device, name, port, pin1, pin2, values, valuestype, node, debug=0):
        self.debug = debug
        self.device = device
        self.name = name
        self.port = str(port)
        self.pin1 = int(pin1)
        self.pin2 = int(pin2)
        self.values = values.split(',')
        self.valuestype = valuestype
        self.node = node
        self.swstate = 0
        if self.debug == 5:
            print("######################################################################")
            print("# Creation du Doubcle Switch {} sur le port {}".format(self.name, self.port))
            print("# du device {} de class {}".format(self.device.devicename, self.device.__class__.__name__))
            print("# Etat du Switch : {}".format(self.getSwitchState()))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 5:
            print("######################################################################")
            print("# Destruction du Double Switch {}".format(self.name))
            print("######################################################################")
            print("\r")

    ###############
    # Methodes
    ###############
    def getValueType(self):
        return self.valuestype

    def getNode(self):
        return self.node

    def getSwitchState(self):
        if self.device.getPin(self.port, self.pin1) == 1:
            self.swstate = self.values[0]
        elif self.device.getPin(self.port, self.pin2) == 1:
            self.swstate = self.values[2]
        else:
            self.swstate = self.values[1]
        return self.swstate


class RotarySwitch:
    """
    Rotary Switch
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    #def __init__(self, device, name, nbpos, port, pins, values, valuestype, node, debug=0):
    def __init__(self, device, name, nbpos, pins, values, valuestype, node, bincode, debug=0):
        self.debug = debug
        self.device = device
        self.name = name
        self.bincode = int(bincode)
        self.nbpos = int(nbpos)
        #self.port = str(port)
        #self.pins = pins.split(',')
        self.pins = {}
        self.pinA = []
        self.maskA = 0
        self.pinB = []
        self.maskB = 0
        self.createPins(pins)
        self.values = values.split(',')
        self.valuestype = valuestype
        self.node = node
        self.pinsvalues = {}
        self.swstate = 0
        if self.debug == 5:
            print("######################################################################")
            print("# Creation du Rotary Switch {}".format(self.name))
            print("# du device {} de class {}".format(self.device.devicename, self.device.__class__.__name__))
            for i in range(0, len(self.pins)):
                print("# Pin {} / Input {} => Value {}".format(i+1, self.pins[i], self.values[i]))
            print("# Etat du Switch : {}".format(self.getSwitchState()))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 5:
            print("######################################################################")
            print("# Destruction du Rotary Switch {}".format(self.name))
            print("######################################################################")
            print("\r")

    ###############
    # Methode
    ###############
    def createPins(self, pins):
        pintab = pins.split(',')
        #for p in range(self.nbpos):
        for p in range(len(pintab)):
            # print("Pos {} {} {}".format(p, pintab[p], type(pintab[p])))
            port = pintab[p][0]
            pin = pintab[p][1]
            self.pins[p] = {'port': port, 'pin': pin}
        #print(self.pins)
        for pin, pindef in self.pins.items():
            if pindef['port'] == 'A':
                self.pinA.append(pindef)
                pinmasknb = int(pindef['pin']) - 1
                pinmask = 1 << pinmasknb
                self.maskA = int(self.maskA) | pinmask
                #print("Pin : {} | Mask Pin Nb: {} | Mask Pin : {}".format(pindef['pin'], pinmasknb, bin(pinmask) ))
            else:
                self.pinB.append(pindef)
                pinmasknb = int(pindef['pin']) - 1
                pinmask = 1 << pinmasknb
                self.maskB = int(self.maskB) | pinmask
                #print("Pin : {} | Mask Pin Nb: {} | Mask Pin : {}".format(pindef['pin'], pinmasknb, bin(pinmask) ))
                
        #print("A => {} : {} [Mask : {}]\nB => {} : {} [Mask : {}]".format(self.pinA, len(self.pinA), bin(self.maskA), self.pinB, len(self.pinB), bin(self.maskB)))

    def getPins(self):
        return self.pins

    def getValues(self):
        return self.values

    def getValueType(self):
        return self.valuestype

    def getNode(self):
        return self.node

    def getSwitchState(self):
        if (self.bincode == 1):
            #print("Reading Rotary Binary Code Switches")
            if len(self.pinA) > 0:
                #print("Reading Port A")
                #print(bin(self.device.getRegister('gpioa')))
                #print(bin(self.device.getRegister('gpioa') & self.maskA))
                swportAval = self.device.getRegister('gpioa') & self.maskA
                if swportBval > 0:
                    #print("Switch Value != 0 : {} | {}".format(bin(swportAval), self.pinA[0]['pin']))
                    strmask = int(self.pinA[0]['pin']) - 1
                    idxval = int(bin(swportAval)[:-strmask], 2)
                else:
                    #print("Switch Value = 0 :{}".format(bin(swportAval)))
                    idxval = 0
            elif len(self.pinB) > 0:
                #print("Reading Port B")
                #print(bin(self.device.getRegister('gpiob')))
                #print(bin(self.device.getRegister('gpiob') & self.maskB))
                swportBval = self.device.getRegister('gpiob') & self.maskB
                if swportBval > 0:
                    #print("Switch Value != 0 : {} | {}".format(bin(swportBval), self.pinB[0]['pin']))
                    strmask = int(self.pinB[0]['pin']) - 1
                    idxval = int(bin(swportBval)[:-strmask], 2)
                else:
                    #print("Switch Value = 0 :{}".format(bin(swportBval)))
                    idxval = 0
            #print("Index Value : {} Len Value : {}".format(idxval, len(self.values)))
            #print(self.values[idxval])
            if (idxval <= (len(self.values) - 1)):
               self.swstate = self.values[idxval]
        else:
            for i in range(0, self.nbpos):
                port = self.pins[i]['port']
                pin = int(self.pins[i]['pin'])
                if self.device.getPin(port, pin) == 1:
                    self.swstate = self.values[i]
        #print(self.swstate)
        return self.swstate

class ToogleSwitch:
    """
    Toogle Switch
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    def __init__(self, device, name, port, pin, values, valuestype, initstate, checknode, node, debug=0):
        self.debug = debug
        self.device = device
        self.name = name
        self.port = str(port)
        self.pin = int(pin)
        self.checknode = int(checknode)
        self.node = node
        self.swstate = initstate
        self.values = values.split(',')
        self.valuestype = valuestype
        self.swstate = self.getTypedData(initstate)
        self.timestamp = datetime.datetime.now()
        if self.debug == 5:
            print("######################################################################")
            print("# Creation du Toogle Switch {} sur le port {}".format(self.name, self.port))
            print("# du device {} de class {}".format(self.device.devicename, self.device.__class__.__name__))
            print("# Etat du Switch : {}".format(self.getSwitchState()))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 5:
            print("######################################################################")
            print("# Destruction du Toogle Switch {}".format(self.name))
            print("######################################################################")
            print("\r")

    ###############
    # Methode
    ###############
    def getMillis(self):
        dt = datetime.datetime.now() - self.timestamp
        ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
        return ms

    def ToogleState(self):
        if self.swstate == self.getTypedData(self.values[0]):
            self.swstate = self.getTypedData(self.values[1])
        else:
            self.swstate = self.getTypedData(self.values[0])
        self.timestamp = datetime.datetime.now()

    def getValueType(self):
        return self.valuestype

    def getTypedData(self, data):
        if self.valuestype == 'string':
            return str(data)
        elif self.valuestype == 'int':
            return int(data)
        elif self.valuestype == 'bool':
            return bool(data)
        else:
            return str(data)
            
    def getInputState(self):
        return self.device.getPin(self.port, self.pin)

    def getSwitchState(self):
        return self.swstate

    def getCheckNode(self):
        return self.checknode

    def getNode(self):
        return self.node

    def setSwitchState(self, value):
        self.swstate = value
        self.timestamp = datetime.datetime.now()
