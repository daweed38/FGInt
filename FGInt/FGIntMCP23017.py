#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import operator
import time

# Standard Modules Import

# Modules Import
from FGIntI2C import I2CDevice

###################################
# FarmerSoft FlightGear Interface
###################################
# MCP23017 Class (Pack I/O)
# FarmerSoft © 2015
# By Daweed
###################################

class MCP23017:
    """
    Cette Class permet la gestion d'un device I2C MCP23017.
    MCP23017 : GPIO Port Expander I2C.
    Copyright FarmerSoft © 2015
    By Daweed
    """

    ###############
    # Properties
    ###############
    registersaddr0 = {
        'iodira': 0x00, 'iopola': 0x02, 'gpintena': 0x04, 'defavala': 0x06, 'intcona': 0x08,
        'iocona' :0x0a, 'gppua': 0x0c, 'intfa': 0x0e, 'intcapa': 0x10, 'gpioa': 0x12, 'olata': 0x14,
        'iodirb': 0x01, 'iopolb': 0x03, 'gpintenb': 0x05, 'defavalb': 0x07, 'intconb': 0x09,
        'ioconb' :0x0b, 'gppub': 0x0d, 'intfb': 0x0f, 'intcapb': 0x11, 'gpiob': 0x13, 'olatb': 0x15
        }

    registersaddr1 = {
        'iodira': 0x00, 'iopola': 0x01, 'gpintena': 0x02, 'defavala': 0x03, 'intcona': 0x04,
        'iocona': 0x05, 'gppua': 0x06, 'intfa': 0x07, 'intcapa': 0x08, 'gpioa': 0x09, 'olata': 0x0a,
        'iodirb': 0x10, 'iopolb': 0x11, 'gpintenb': 0x12, 'defavalb': 0x13, 'intconb': 0x14,
        'ioconb' :0x15, 'gppub': 0x16, 'intfb': 0x17, 'intcapb': 0x18, 'gpiob': 0x19, 'olatb': 0x1a
            }

    maskup = {
        1: 0b00000001, 2: 0b00000010, 3: 0b00000100, 4: 0b00001000,
        5: 0b00010000, 6: 0b00100000, 7: 0b01000000, 8: 0b10000000
        }

    maskdown = {
        1: 0b11111110, 2: 0b11111101, 3: 0b11111011, 4: 0b11110111,
        5: 0b11101111, 6: 0b11011111, 7: 0b10111111, 8: 0b01111111
        }

    ###############
    # Constructor
    ###############
    def __init__(self, devicename, deviceaddr, debug=0):
        self.debug = debug
        self.devicename = devicename
        self.deviceaddr = int(deviceaddr, 16)
        self.devicetype = 'MCP23017'
        self.registeraddrbank = self.registersaddr0
        self.bankmode = 0 
        self.state = 0
        self.pullup = 0
        self.i2c = I2CDevice(self.devicename, self.deviceaddr, self.debug)
        if self.debug == 2:
            print("######################################################################")
            print("# Initialisation du Device {} à l'adresse {}".format(self.devicename, hex(self.deviceaddr)))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 2:
            print("######################################################################")
            print("# Destruction du Device {}".format(self.devicename))
            print("######################################################################")
            print("\r")
        self.configMCP(0)

    ###############
    # Methods
    ###############
    
    # Configuration
    def configMCP(self, state):
        if state == 1:
            if self.debug == 2:
                print("######################################################################")
                print("# Activation du device {}".format(self.devicename))
                print("######################################################################")
                print("\r")
        else:
            if self.debug == 2:
                print("######################################################################")
                print("# Reset des Registre")
                print("# Desactivation du device {}".format(self.devicename))
                print("######################################################################")
                print("\r")
            self.ResetRegisters()

    def ResetRegisters(self):
        for register in self.registeraddrbank:
            if register == 'iodira' or register == 'iodirb':
                if self.debug == 2:    
                    print("######################################################################")
                    print("# IODIRA / IODIRB {}".format(register, self.getRegisterAddr(register)))
                    rint("######################################################################")
                self.setRegister(register, 0xff)
            else:
                if self.debug == 2:
                    print("######################################################################")
                    print("# AUTRES {}".format(register, self.getRegisterAddr(register)))
                    print("######################################################################")
                self.setRegister(register, 0x00)


    def setModeBank(self, bankmode):
        self.bankmode = bankmode
        if self.bankmode == 1:
            self.setBit('iocona', 8, 1)
            self.registeraddrbank = self.registersaddr1
        else:
            self.setBit('iocona', 8, 0)
            self.registeraddrbank = self.registersaddr0

    # getName()
    # return device name
    def getName(self):
        return self.devicename

    # getType()
    # return device type
    def getType(self):
        return self.devicetype

    # getAddress()
    # return device address 
    def getAddress(self):
        return hex(self.deviceaddr)


    # Systeme
    def getRegisterAddr(self, register):
        registeraddr = self.registeraddrbank[register]
        if self.debug == 2:
            print("######################################################################")
            print("# Adresse du registre {} : {} sur le device {}".format(register, hex(registeraddr), self.devicename))
            print("######################################################################")
            print("\r")
        return registeraddr

    def getRegister(self, register):
        registeraddr = self.getRegisterAddr(register)
        registervalue = self.i2c.readRegister(registeraddr)
        if self.debug == 2:
            print("######################################################################")
            print("# Lecture du registre {} ({}) : {}".format(register, hex(registeraddr), bin(registervalue)))
            print("######################################################################")
            print("\r")
        return registervalue

    def setRegister(self, register, registervalue):
        registeraddr = self.getRegisterAddr(register)
        if self.debug == 2:
            print("######################################################################")
            print("# Ecriture de la valeur {} dans le registre {} à l'adresse {}".format(bin(registervalue), register, hex(registeraddr)))
            print("######################################################################")
            print("\r")
        self.i2c.writeRegister(registeraddr, registervalue)

    def getBit(self, register, bit):
        mask = self.maskup[bit]
        registervalue = self.getRegister(register)
        value = registervalue & mask
        if value > 0:
            state = 1
        else:
            state = 0
        if self.debug == 2:
            print("######################################################################")
            print("# Lecture de l'entree {} sur le registre {} : {}".format(bit, register, value))
            print("# Masque de lecture : {}".format(bin(mask)))
            print("# Etat de l'entree : {}".format(state))
            print("######################################################################")
            print("\r")
        return state

    def setBit(self, register, bit, value):
        if value == 1:
            mask = self.maskup[bit]
            registervalue = self.getRegister(register) | mask
        else:
            mask = self.maskdown[bit]
            registervalue = self.getRegister(register) & mask
        registeraddr = self.getRegisterAddr(register)
        
        if self.debug == 2:
            print("######################################################################")
            print("# Modification du bit {} vers l'etat {} sur le registre {}".format(bit, value, register))
            print("######################################################################")
            print("\r")
        self.i2c.writeRegister(registeraddr, registervalue)

    # Interruption Management
    def setPortInterrupt(self, port, interrup):
        if port == 'A':
            register = 'gpintena'
        else:
            register = 'gpintenb'
        if interrup  == 1:
            registervalue = 0xff
        else:
            registervalue = 0x00
        registeraddr = self.getRegisterAddr(register)
        self.i2c.writeRegister(registeraddr, registervalue)

    def getDefaultCompare(self, port):
        if port == 'A':
            register = 'defvala'
        else:
            register = 'defvalb'
        registeraddr = self.getRegisterAddr(register)
        return self.i2c.readRegister(registeraddr)

    def setDefaultCompare(self, port, default):
        if port == 'A':
            register = 'defvala'
        else:
            register = 'defvalb'
        registeraddr = self.getRegisterAddr(register)
        self.i2c.writeRegister(registeraddr, default)

    def getCompareMode(self, port):
        if port == 'A':
            register = 'intcona'
        else:
            register = 'intcona'
        registeraddr = self.getRegisterAddr(register)
        return self.i2c.readRegister(registeraddr)

    def setCompareMode(self, port, compmode):
        if port == 'A':
            register = 'intcona'
        else:
            register = 'intconb'
        registeraddr = self.getRegisterAddr(register)
        self.i2c.writeRegister(registeraddr, default)

    def getInterrupFlag(self, port):
        if port == 'A':
            register = 'intfa'
        else:
            register = 'intfb'
        registeraddr = self.getRegisterAddr(register)
        return self.i2c.readRegister(registeraddr)

    def getInterrupData(self, port):
        if port == 'A':
            register = 'intcapa'
        else:
            register = 'intcapb'
        registeraddr = self.getRegisterAddr(register)
        return self.i2c.readRegister(registeraddr)

        # Pull Up Resistor Management
    def setPullUpRegister(self, port, pullup):
        if port == 'A':
            register = 'gppua'
        else:
            register = 'gppub'
        if pullup == 1:
            registervalue = 0xff
        else:
            registervalue = 0x00
        registeraddr = self.getRegisterAddr(register)
        self.i2c.writeRegister(registeraddr, registervalue)


    # Polarity GPIO Management
    def setGpioPolarity(self, port, polarity):
        if port == 'A':
            register = 'iopola'
        else:
            register = 'iopolb'
        if pullup == 1:
            registervalue = 0xff
        else:
            registervalue = 0x00
        registeraddr = self.getRegisterAddr(register)
        self.i2c.writeRegister(registeraddr, registervalue)

    # GPIO Port Management
    def setPortDirection(self, port, direction):
        if port == 'A':
            register = 'iodira'
        else:
            register = 'iodirb'
        if direction == 'out':
            registervalue = 0x00
            dirname = 'output'
        else:
            registervalue = 0xff
            dirname = 'input'
        if self.debug == 2:
            print("######################################################################")
            print("# Configuration des pin du port {} en {}".format(port, dirname))
            print("# Adresse du Port : {}".format(hex(self.getRegisterAddr(register))))
            print("# Valeur Inscrite : {}".format(hex(registervalue)))
            print("######################################################################")
            print("\r")
        self.setRegister(register, registervalue)

    # GPIO Pin Management
    def setPinDirection(self, port, pin, direction):
        if port == 'A':
            register = 'iodira'
        else:
            register = 'iodirb'
        if direction == 'out':
            dirname = 'output'
            state = 0
        else:
            dirname = 'input'
            state = 1
        if self.debug == 2:
            print("######################################################################")
            print("# Pin {} sur le Port {} à été configuré en {}".format(pin, port, dirname))
            print("######################################################################")
            print("#\r")
        self.setBit(register, pin, state)

    def getPin(self, port, pin):
        if port == 'A':
            register = 'gpioa'
        else:
            register = 'gpiob'
        return self.getBit(register, pin)

    def setPin(self, port, pin, value):
        if port == 'A':
            register = 'olata'
        else:
            register = 'olatb'
        self.setBit(register, pin, value)
