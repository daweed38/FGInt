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
# HT16K33 Class (Pack LED)
# FarmerSoft © 2015
# By Daweed
###################################

class HT16K33:
    """
    This class allow the HT16K33 object creation
    to manage an HT16K33 I2C hardware device
    HT16K33 : Backpack LED I2C.
    Copyright FarmerSoft © 2017
    By Daweed
    """

    ###############
    # Properties
    ###############
    systemregster = 0x20
    displayregister = 0x80
    brightregigtser = 0xe0

    blinkoff = 0x00
    blink2hz = 0x02
    blink1hz = 0x04
    blinkhlf = 0x06

    comregisters = {
        1: 0x00, 2: 0x01, 3: 0x02, 4: 0x03,
        5: 0x04, 6: 0x05, 7: 0x06, 8: 0x07,
        9: 0x08, 10: 0x09, 11: 0x0A, 12: 0x0B,
        13: 0x0C, 14: 0x0D, 15: 0x0E, 16: 0x0F
    }

    RegistersA = {
        1:0x00, 2:0x02, 3:0x04, 4:0x06, 5:0x08, 6:0x0A, 7:0x0C, 8:0x0E
    }

    RegistersB = {
        1:0x01, 2:0x03, 3:0x05, 4:0x07, 5:0x09, 6:0x0B, 7:0x0D, 8:0x0F
    }

    ###############
    # Constructor
    ###############
    def __init__(self, devicename, deviceaddr, debug=0):
        self.debug = debug
        self.devicename = devicename
        self.deviceaddr = deviceaddr
        self.devicetype = 'HT16K33'
        self.state = 0
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

    ###############
    # System Methods
    ###############
    
    # Methode configMCP(state)
    # Cette methode permet d activer ou de désactiver le device
    def configMCP(self, state):
        if state == 1:
            if int(self.debug) == 2:
                print("######################################################################")
                print("# Activation du device {}".format(self.devicename))
                print("######################################################################")
                print("\r")
            self.i2c.writeRegister(0x21, 0x00)
            for i in self.comregisters:
                self.i2c.writeRegister(self.comregisters[i], 0x00)
        else:
            if int(self.debug) == 2:
                print("######################################################################")
                print("# Desactivation du device {}".format(self.devicename))
                print("######################################################################")
                print("\r")
            for i in self.comregisters:
                self.i2c.writeRegister(self.comregisters[i], 0x00)
            self.i2c.writeRegister(0x20, 0x00)
        self.Stop()

    # Methode Start()
    # Permet d'activer l'oscillateur du device
    def Start(self):
        if self.state != 1:
            self.state = 1
            self.i2c.writeRegister(0x81, 0x00)
        return self.state

    # Methode Stop()
    # Desactive l'oscillateur du device
    def Stop(self):
        if self.state != 0:
            self.state = 0
            self.i2c.writeRegister(0x80, 0x00)
        return self.state

    # getStatus()
    def getStatus(self):
        return self.state

    # Methode getComRegister(com)
    def getComRegister(self, com):
        return self.comregisters[com]
    
    # Methode getComPortRegister(port, com)
    def getComPortRegister(self, port, com):
        if port == 'A':
            return self.RegistersA[com]
        else:
            return self.RegistersB[com]
        
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
        return self.deviceaddr

    # Methode setBrightness(brightness)
    # Permet de Regler la luminosité des Sorties
    # du HT16K33
    def setBrightness(self, brightness):
        registeraddr = self.brightregigtser | int(brightness)
        if int(self.debug) == 2:
            print("######################################################################")
            print("# Modification de Luminosité : {} => Registre : {}".format(brightness, registeraddr))
            print("######################################################################")
            print("\r")
        self.i2c.writeRegister(registeraddr, 0x00)

    # setBlinkRate(blinkrate)
    # Permet de Relgler la frequence de clignottement 
    # des Sorties du HT16K33
    def setBlinkRate(self, blinkrate):
        if int(self.state) == 0:
            systregister = 0x80
        else:
            systregister = 0x81

        if blinkrate == "blinkoff":
            blinkratevalue = 0x00
        elif blinkrate == "blink2hz":
            blinkratevalue = 0x02
        elif blinkrate == "blink1hz":
            blinkratevalue = 0x04
        elif blinkrate == "blinkhlf":
            blinkratevalue = 0x06
        else:
            blinkratevalue = 0x00
            
        registeraddr = systregister | blinkratevalue
        if int(self.debug) == 2:
            print("######################################################################")
            print("# Modification de la fréquence de clignoteement : {}".format(blinkrate))
            print("######################################################################")
            print("\r")
        self.i2c.writeRegister(registeraddr, 0x00)

    # clearBuffers()
    # Permet de remettre à zero tous les buffers
    # de sortie du HT16K33
    def clearAllBuffer(self):
        if int(self.debug) == 2:
            print("######################################################################")
            print("# Réinitialisation des Buffer de Sortie (0x00 Partout)")
            print("######################################################################")
            print("\r")
        for i in self.comregisters:
            self.i2c.writeRegister(self.comregisters[i], 0x00)

    # clearBuffer(register)
    # Permet de mettre a zero un buffer
    # de sortie du HT16K33
    def clearBuffer(self, register):
        if int(self.debug) == 2:
            print("######################################################################")
            print("# Réinitialisation du Buffer de Sortie {} a zero (0x00)".format(register))
            print("######################################################################")
            print("\r")
        self.i2c.writeRegister(self.comregisters[register], 0x00)

    # setRow(row, data)
    # Permet de Mettre à jour le buffer de Sortie
    # d'une rangé du HT16K33
    def setRow(self, port, row, data):
        if port == "A":
            registeraddr = self.RegistersA[row]
        elif port == "B":
            registeraddr = self.RegistersB[row]
        else:
            registeraddr = None
        if int(self.debug) == 9:
            print("######################################################################")
            print("# Update Row {} sur le Port {} avec la valeur {} [ {} en Hexa ]".format(row, port, bin(data), hex(data)))
            print("# Register Addr : {}".format(hex(registeraddr)))
            print("######################################################################")
            print("\r")
        if registeraddr != None:
            self.i2c.writeRegister(registeraddr, data)

    # setOut(row, out, value)
    # Permet de Mettre à jour de la sortie dans un row
    def setOut(self, port, row, out, value):
        if port == "A":
            registeraddr = self.RegistersA[row]
        elif port == "B":
            registeraddr = self.RegistersB[row]
        else:
            registeraddr = None
        if int(self.debug) == 2:
            print("######################################################################")
            print("# Mise à jour de la sortie {} dans la rangé {} avec l'état {}".format(out, row, value))
            print("# Com Register Addr : {}".format(hex(registeraddr)))
            print("######################################################################")
            print("\r")
        if int(row) != 0:
            self.i2c.writeBit(registeraddr, out, value)
