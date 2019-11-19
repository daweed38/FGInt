#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import operator
import time

# Standard Modules Import

###################################
# FarmerSoft FlightGear Interface
###################################
# DISPLAY Class (Affichage)
# FarmerSoft © 2015
# By Daweed
###################################

class SegDisplay:
    """
    This class allow Segment Display management
    based on hardware driver HT16K33
    Copyright FarmerSoft © 2017
    By Daweed
    """

    ###############
    # Properties
    ###############
    digitnumber = {
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F,
        '4': 0x66, '5': 0x6D, '6': 0x7D, '7': 0x07,
        '8': 0x7F, '9': 0x6F, 'A': 0x77, 'B': 0x7C,
        'C': 0x39, 'D': 0x5E, 'E': 0x79, 'F': 0x71,
        '-': 0x40, 'S': 0x6D, 't': 0x78, 'd': 0x5e,
        ' ' : 0x00, 'a': 0x77
        }

    ###############
    # Constructor
    ###############
    def __init__(self, device, name, nbdigit, port, com1, decdigit, debug=0):
        self.debug = debug
        self.device = device
        self.dispname = name
        self.disptype = 'Segment Display'
        self.nbdigit = int(nbdigit)
        self.port = port
        self.com1 = int(com1)
        self.decdigit = int(decdigit) + 1
        self.value = ''
        self.status = 'OFF'
        if self.debug == 9:
            print("######################################################################")
            print("# Création d'un afficheur 7 segments {} avec {} digit(s)".format(self.dispname, self.nbdigit))
            print("# Registre premier Digit: {}".format(hex(self.device.getComPortRegister(self.port, self.com1))))
            print("# sur le device {}".format(self.device.devicename))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 9:
            print("######################################################################")
            print("# Destruction de l'afficheur 7 segments {}".format(self.dispname))
            print("######################################################################")
            print("\r")

    ###############
    # Methods
    ###############

    ## System Methods

    # Method getName()
    # Return Display Name
    def getName(self):
        return self.dispname

    # Method getType()
    # Return Display Type
    def getType(self):
        return self.disptype

    # Method getDigitNumber()
    # Return the Number of digit
    def getDigitNumber(self):
        return self.nbdigit

    # Method getStatus()
    # Return Display Status
    def getStatus(self):
        return self.status

    # Methode getDigitRegister(digit)
    # Cette methode renvoie l'adresse du regitre
    # d'un digit de l'afficheur
    def getDigitRegister(self, digit):
        comregister = self.com1 + (digit - 1)
        registeraddr = self.device.getComPortRegister(self.port, comregister)
        if self.debug == 9:
            print("######################################################################")
            print("# Digit {} sur le port {} sur le Com {}".format(digit, self.port, comregister))
            print("# Adresse du Registre {}".format(hex(registeraddr)))
            print("######################################################################")
            print("\r")
        return registeraddr

    def setStatus(self, status):
        if self.debug == 9:
            print("######################################################################")
            print("# Display Set to {} Status".format(status))
            print("######################################################################")
            print("\r")
        if self.getStatus() != status:
            if status == 'OFF':
                value = ''
                for i in range(1, int(self.nbdigit) + 1):
                    value = value + ' '
                self.writeDisplay(value, 0)
                self.status = status
            elif status == 'ON':
                self.status = 'ON'
            else:
                return

    # Methode ListDigitsRegister()
    # Cette methode renvoie la liste des adresses
    # des digits de l'afficheur
    def listDigitsRegister(self):
        for i in range(1, int(self.nbdigit) + 1):
            print("# Digit {} à l'adresse {}".format(i, hex(self.getDigitRegister(i))))
            print("\r")

    # Methode writeDigit(digit, digitvalue)
    # Cette methode affiche la valeur digitvalue
    # sur le digit 
    def writeDigit(self, digit, digitvalue, decimal):
        row = int(self.com1) + (digit - 1)
        if self.debug == 9:
            print("######################################################################")
            print("# Ecriture de la Valeur {} sur le Digit {} sur le Port {}".format(digitvalue, digit, self.port))
            print("# Valeur à mettre dans le Registre : {}".format(hex(self.digitnumber[str(digitvalue)])))
            print("# Adresse du Registre du Digit : {}".format(hex(self.getDigitRegister(digit))))
            print("######################################################################")
            print("\r")
        basevalue = self.digitnumber[str(digitvalue)]
        if decimal == 1:
            newvalue = int(self.digitnumber[str(digitvalue)]) | 0b10000000
            self.device.setRow(self.port, row, newvalue)
        else:
            self.device.setRow(self.port, row, self.digitnumber[str(digitvalue)])
            
        

    # Methode def writeDisplay(value)
    # Cette methode affiche la valeur value
    # sur l'afficheur (Zero Fill)
    def writeDisplay(self, value, decimal):
        dispvalue = str(value).zfill(self.nbdigit)
        self.value = dispvalue
        datadigit = map(str, str(value).zfill(self.nbdigit))
        digit = 1
        #digit = self.nbdigit
        if self.debug == 9:
            print("######################################################################")
            print("# Ecriture de la valeur {} sur l'afficheur {}".format(value, self.dispname))
            print("# Valeur Zero Fill : {} [ Type : {} ]".format(dispvalue, type(dispvalue)))
            print("# Type de datadigit : {}".format(type(datadigit)))
            print("# Liste des Adresse de registre : ")
        #for digitvalue in reversed(datadigit):
        for digitvalue in datadigit:
            if self.debug == 9:
                print("#    Digit {} à l'adresse {} Value {}. com1 : {}".format(digit, hex(self.getDigitRegister(digit)), digitvalue, self.com1))
                print("#")
            if digit > 0:
                if digit == (self.decdigit - 1) and int(decimal) == 1:
                    self.writeDigit(digit, digitvalue, 1)
                else:
                    self.writeDigit(digit, digitvalue, 0)
            digit += 1
        if self.debug == 9:
            print("#")
            print("######################################################################")
            print("\r")
