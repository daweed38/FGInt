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

class SwitchLight:
    """
    Cette Class hérite de la Class de gestion des LED Pack HT16K33.
    Elle permet la gestion des témoin lumineux d'un switch.
    Copyright FarmerSoft 2014 (c)
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    def __init__(self, device, lightname, nblight, port, row, out1, prop, initstate, activemode, debug=0):
        self.debug = debug
        self.device = device
        self.lightname = lightname
        self.nblight = int(nblight)
        self.port = str(port)
        self.row = int(row)
        self.out1 = int(out1)
        self.prop = prop
        self.activemode = int(activemode)
        self.state = initstate
        if self.debug == 4:
            print("######################################################################")
            print("# Création du Groupe de Temoin(s) Lunimeux {} sur le Port {}".format(self.lightname, self.port))
            print("# sur le device de class {}".format(self.device.__class__.__name__))
            print("# Pin out1  : {}".format(self.out1))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if self.debug == 4:
            print("######################################################################")
            print("# Destruction du Groupe Temoin(s) Lumineux {}".format(self.lightname))
            print("######################################################################")
            print("\r")

    ###############
    # Methods
    ###############
    # Method getName()
    # Return the Switch Light Name
    def getName(self):
        return self.lightname

    # Method getLightState()
    # Return the Switch Light State
    def getLightState(self):
        return self.state

    # Method getProperty()
    # Return the Flightgear Property that have been
    # configured to manage the Switch Light
    def getProperty(self):
        return self.prop

    # Method setLightState(state)
    # Set the Switch Light in the state 'state' 
    # state  = 'ON' or 'OFF'
    def setLightState(self, state):
        self.state = state
        if self.debug == 4:
            print("Updating Switch Lite to : {}".format(state))
        if self.activemode == 1:
            if self.state == 'ON':
                self.device.setOut(self.port, self.row, self.out1, 1)
            elif self.state == 'OFF':
                self.device.setOut(self.port, self.row, self.out1, 0)
            else:
                return false
        else:
            if self.state == 'ON':
                self.device.setOut(self.port, self.row, self.out1, 0)
            elif self.state == 'OFF':
                self.device.setOut(self.port, self.row, self.out1, 1)
            else:
                return false
