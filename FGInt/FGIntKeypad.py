#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import operator
import time

import RPi.GPIO as GPIO

# Standard Modules Import

###################################
# FarmerSoft FlightGear Interface
###################################
# DISPLAY Class (Affichage)
# FarmerSoft © 2015
# By Daweed
###################################

class Keypad:
    """
    This class allow Keypad management
    based on hardware driver HT16K33
    Copyright FarmerSoft © 2020
    By Daweed
    """

    ###############
    # Properties
    ###############
    rowsaddrA = [0x40, 0x42, 0x44]
    rowsaddrB = [0x41, 0x43, 0x45]

    ###############
    # Constructor
    ###############
    def __init__(self, device, name, port, com1, row1, nbcol, nbrow, intpin, matrix, bounce, debug=0):
        self.debug = debug
        self.device = device
        self.port = port
        self.com1 = com1
        self.dispname = name
        self.disptype = 'Keypad'
        if self.port == 'A':
            self.rowsaddr = self.rowsaddrA
        else:
            self.rowsaddr = self.rowsaddrB
        self.nbcol = int(nbcol)
        self.nbrow = int(nbrow)
        self.matrix = []
        self.createMatrix(matrix.split(','))
        self.keypressed = 0
        self.keyval = ''
        self.bounce = int(bounce)
        self.intpin = int(intpin)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.intpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.intpin, GPIO.RISING, self.catchKey, bouncetime=self.bounce)
        self.device.getInterRegister()
        self.device.i2c.ReadRegister(0x40)
        self.device.i2c.ReadRegister(0x41)
        self.device.i2c.ReadRegister(0x42)
        self.device.i2c.ReadRegister(0x43)
        self.device.i2c.ReadRegister(0x43)
        self.device.i2c.ReadRegister(0x45)
        if (self.debug == 10):
            print("######################################################################")
            print("Keypad {} creation {} col x {} row".format(self.dispname, self.nbcol, self.nbrow))
            print("on device {}".format(self.device.devicename))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 10:
            print("######################################################################")
            print("# Keypad {} destruction".format(self.dispname))
            print("######################################################################")
            print("\r")

    ###############
    # Methods
    ###############

    def getInterRegister(self):
        return self.device.getInterRegister()

    def catchKey(self, pin):
        if (self.getInterRegister() != 0 and self.keypressed == 0):
            for row in range(len(self.rowsaddr)):
                rowval = self.device.i2c.ReadRegister(self.rowsaddr[row])
                #print("Reading Line {} addr : {} value : {} Inter Register : {}".format(
                #    row, hex(self.rowsaddr[row]), bin(rowval).zfill(8), self.getInterRegister()
                #))
                if rowval != 0:
                    idxval = rowval >> 1
                    self.keyval = self.matrix[row][idxval]
                    #print("Row {} Row Value : {} Index Key Value {} Key Value {}".format(
                    #    row, rowval, idxval, keyval
                    #))
                    self.keypressed = 1

    def getKeyPressed(self):
        return self.keypressed

    def getKey(self):
        self.keypressed = 0
        keyval = self.keyval
        self.keyval = ''
        return keyval

    def createMatrix(self, matrixdata):
        if (self.debug == 10):
            print(matrixdata)
            print(type(self.matrix))
        i = 0
        for row in range(self.nbrow):
            if (self.debug == 10):
                print("Row : {}".format(row))
            self.matrix.append([])
            for col in range(self.nbcol):
                if (self.debug == 10):
                    print("Col : {} => {}".format(col, matrixdata[i]))
                self.matrix[row].append(matrixdata[i])
                i = i + 1

    def getMatrix(self):
        return self.matrix
