#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import operator
import time

# Standard Modules Import
import re
import smbus

###################################
# FarmerSoft FlightGear Interface
###################################
# I2C Class (I2C Bus Devices)
# FarmerSoft © 2015
# By Daweed
###################################

class I2CBus:
    """
    Cette Classe permet la gestion du bus I2C
    Copyright FarmerSoft @ 2017
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    def __init__(self, debug=0):
        self.debug = debug
        self.busnum = self.getPiI2CBusNumber()
        self.i2c = smbus.SMBus(self.busnum)
        self.devices = []
        #self.i2cdetect()

    ###############
    # Destructor
    ###############
    def __del__(self):
        print("Destruction du Bus I2")

    ###############
    # Methods
    ###############

    # Recupere la Version du RPi
    @staticmethod
    def getPiRevision():
        # "Gets the version number of the Raspberry Pi board"
        # Courtesy quick2wire-python-api
        # https://github.com/quick2wire/quick2wire-python-api
        # Updated revision info from: http://elinux.org/RPi_HardwareHistory#Board_Revision_History
        try:
            with open('/proc/cpuinfo','r') as f:
                for line in f:
                    if line.startswith('CPU revision'):
                        return 1 if line.rstrip()[-1] in ['2','3'] else 2
        except:
            return 0

    # Recupere le N° de Bus I2C en fonction de la version du RPi
    @staticmethod
    def getPiI2CBusNumber():
        # Gets the I2C bus number /dev/i2c#
        return 1 if I2CBus.getPiRevision() > 1 else 0

    # i2cdetect Function detect & send slave device discovered
    def i2cdetect(self):
        first = 0x03
        last = 0x77
        self.devices = []
        #print('Bus: I2C-{}\n'.format(self.bus))
        #print("      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")
        for i in range(0, 128, 16):
            #print(' {0:02x}: '.format(i), end='')
            for j in range(0, 16):
                address = int(i) + j
                res = None
                if address < first or address > last:
                    #print("   ", end='')
                    continue
                try:
                    res = self.i2c.read_byte(address)
                except OSError as error:
                    pass
                finally:
                    if res is not None:
                        print(address)
                        self.devices.append(hex(address))
                        #print('{0:02x} '.format(address), end='')
                    else:
                        #print('-- ', end='')
                        pass
            #print('')
        #print('')
        return self.devices

    def getDevices(self):
        return self.devices


class I2CDevice(I2CBus):
    """
    Cette Classe permet la gestion d'un device sur le bus I2C.
    Copyright FarmerSoft © 2015.
    """

    ###############
    # Properties
    ###############
    
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
        super().__init__()
        self.debug = debug
        self.bus = self.getPiI2CBusNumber()
        self.devicename = devicename
        self.deviceaddr = deviceaddr
        self.i2c = smbus.SMBus(self.bus)
        if int(self.debug) == 3:
            print("######################################################################")
            print("# Initialisation du Device I2C {} à l'adresse {}".format(self.devicename, hex(self.deviceaddr)))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if int(self.debug) == 3:
            print("######################################################################")
            print("# Destruction du Device I2C {}".format(self.devicename))
            print("######################################################################")
            print("\r")

    ###############
    # Methods
    ###############
    # getDeviceName()
    # Return the Device Name
    def getDeviceName(self):
        return self.devicename

    # getDeviceAddr()
    # Return the Device Address
    def getDeviceAddr(self):
        return hex(self.deviceaddr)

    # readRegister(registeraddr)
    # Retourne la valeur d'un registre à l'adresse 'registeraddr'
    def readRegister(self, registeraddr):
        regval = self.i2c.read_byte_data(self.deviceaddr, registeraddr)
        if int(self.debug) == 3:
            print("######################################################################")
            print("# Type de la variable registeraddr pendant : {}".format(type(registeraddr)))
            print("# Lecture du registre à l'adresse {} : {}".format(hex(registeraddr),bin(regval)))
            print("######################################################################")
            print("\r")
        return regval

    # writeRegister(registeraddr, registervalue)
    # Ecrit la valeur registervalue dans le registre à l'adresse registeraddr
    def writeRegister(self, registeraddr, registervalue):
        if int(self.debug) == 3:
            print("######################################################################")
            print("# Ecriture de {} dans le registre à l'adresse {} sur le device {}".format(
                hex(registervalue), 
                hex(registeraddr), 
                self.devicename
                ))
            print("######################################################################")
            print("\r")
        return self.i2c.write_byte_data(self.deviceaddr, registeraddr, registervalue)

    # Methode readBit(registeraddr, bit)
    def readBit(self, registeraddr, bit):
        mask = self.maskup[bit]
        if self.readRegister(registeraddr) & mask > 0:
            bitvalue = 1
        else:
            bitvalue = 0
        if int(self.debug) == 3:
            print("######################################################################")
            print("# Lecture du Bit {} dans le registre à l'adresse {} : {}".format(
                bit,
                hex(registeraddr),
                bitvalue
                ))
            print("######################################################################")
            print("\r")
        return bitvalue

    # Methode writeBit(self, registeraddr, bit, state)
    def writeBit(self, registeraddr, bit, state):
        registerdata = self.readRegister(registeraddr)
        if state == 1:
            maskname = 'maskup'
            mask = self.maskup[bit]
            operation = 'OR'
            newregisterdata = registerdata | mask
        else:
            maskname = 'maskdown'
            mask = self.maskdown[bit]
            operation = 'AND'
            newregisterdata = registerdata & mask
        if int(self.debug) == 3:
            print("######################################################################")
            print("# Mask Type : {} Mask {} Operation : {}".format(maskname, bin(mask), operation))
            print("# Ecriture de la valeur {} sur le bit {} dans le registre à l'adresse {}".format(
                state,
                bit,
                hex(registeraddr)    
                ))
            print("######################################################################")        
            print("\r")
        self.writeRegister(registeraddr, newregisterdata)
