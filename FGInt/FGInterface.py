#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import operator
import time

# Standard Modules Import
import configparser
import importlib

# FarmerSoft Actor Class Import

###################################
# FarmerSoft FlightGear Interface
###################################
# FarmerFGInt Class
# FarmerSoft © 2016
# By Daweed
###################################

class FGInterface:
    """
    This Class is the main interface structure class
    From this Class all is available
    The FarmerFGInt object is created with the configuration files 
    """

    ###############
    # Properties
    ###############

    ###############
    # Constructor
    ###############
    def __init__(self, configfile, debug=0):
        self.debug = int(debug)
        self.configfile = configfile
        self.configfullpath = "/opt/fgint/Config/" + configfile
        self.config = {}
        self.modules = {}
        self.devices = {}
        self.auxconf = {}
        self.elements = {}
        self.config = self.readConfig()
        self.intname = self.getConfigOption('INT', 'intname')
        
        if int(self.debug) == 1:
            print("######################################################################")
            print("# Init FGInterface")
            print("######################################################################")
            print("# Interface Creation {}".format(self.intname))
            print("# Configuration File : {}".format(self.configfullpath))
            print("######################################################################")
            print("\r")

    ###############
    # Destructor
    ###############
    def __del__(self):
        if int(self.debug) == 1:
            print("######################################################################")
            print("# Interface Destruction {}".format(self.intname))
            print("######################################################################")
            print("\r")

    ###################################
    ## System Methods
    ###################################

    # getName()
    # return the interface name
    def getName(self):
        return self.intname

    # getConfigFile()
    # return the full configuration file
    # path used to create the interface
    def getConfigFile(self):
        return self.configfullpath
    
    # readConfig()
    # read & store the interface configuration
    def readConfig(self):
        if self.debug == 1:
            print("##################################################")
            print("#")
        self.config = {}
        Config = configparser.ConfigParser()
        Config.read(self.configfullpath)
        for section in Config.sections():
            if self.debug == 1:
                print("# Section : {}".format(section))
            optiontab = {}
            for option in Config.options(section):
                if self.debug == 1:
                    print("# - Option : {} => Value : {}".format(option, Config[section][option]))
                optiontab[option] = Config[section][option]
            self.config[section] = optiontab

        if 'MODULES' in self.config:
            self.loadModules()
            if self.debug == 1:
                print(self.modules)

        #print(self.config)

        self.createDevices()

        if 'AUXCONF' in self.config:
            self.loadAuxConfigs()

        if self.debug == 1:
            print("#")
            print("##################################################")
            print("\r")

        return self.config

    # getConfig()
    # return interface config
    def getConfig(self):
        return self.config

    # getConfigSection(section)
    # return interface section config
    def getConfigSection(self, section):
        return self.config[section]

    # getOption(section, option)
    # return interface option config
    def getConfigOption(self, section, option):
        return self.config[section][option]

    # getDebugLevel()
    # return Debug Level
    def getDebugLevel(self):
        return self.debug

    # setDebugLevel(debuglevel)
    # set the Debug level to debuglevel
    def setDebugLevel(self, debuglevel):
        if self.debug == 1:
            print("##################################################")
            print("# Set Debug to {}".format(debuglevel))
            print("##################################################")
            print("\r")
        self.debug = int(debuglevel)

    ###################################
    ## Modules Methods
    ###################################

    # listModules()
    # return a modules configuration
    def listModules(self):
        return self.config['MODULES']

    # listLoadedModule()
    # return loaded modules
    def listLoadedModules(self):
        return self.modules

    # loadModules()
    # load modules from configuration
    def loadModules(self):
        self.modules = {}
        for moduleconf in self.listModules().items():
            package = moduleconf[1].split(',')[0]
            module = moduleconf[1].split(',')[1]
            self.modules[module] = importlib.import_module(package)

    # getModule(modulename)
    # return module object by name
    def getModule(self, modulename):
        return getattr(self.modules[modulename], modulename)

    ###################################
    ## Devices Methods
    ###################################

    # getDeviceConf(devicename)
    # return device configuration
    def getDeviceConf(self, devicename):
        return self.devices[devicename]['CONF']

    # getDevice(devicename)
    # return device object
    def getDevice(self, devicename):
        return self.devices[devicename]['OBJECT']

    # listDevices()
    # return devices list from configuration
    def getDevices(self):
        return self.devices

    # createDevice(devicename)
    # create & store device object
    def createDevice(self, devicename):
        if self.debug == 1:
            print("#")
            print("# Device Config : {}".format(self.config['INT']['deviceconf']))
            print("# Creating device ... ")
            print("#")
        deviceconfig = configparser.ConfigParser()
        deviceconfig.read(self.config['INT']['deviceconf'])
        self.devices[devicename] = {}
        self.devices[devicename]['CONF'] = {}
        if self.debug == 1:
            print("# Device : {}".format(devicename))
        for option in deviceconfig.options(devicename):
            if self.debug == 1:
                print("# - {} : {}".format(option, deviceconfig[devicename][option]))
            self.devices[devicename]['CONF'][option] = deviceconfig[devicename][option]
        mod = self.getModule(deviceconfig[devicename]['devicetype'])
        self.devices[devicename]['OBJECT'] = mod(deviceconfig[devicename]['devicename'], str(deviceconfig[devicename]['deviceaddr']), self.debug)
        return self.devices[devicename]['OBJECT']

    # createDevices()
    # create & store devices defined in configuration
    def createDevices(self):
        deviceconfig = configparser.ConfigParser()
        deviceconfig.read(self.config['INT']['deviceconf'])
        conftab = ['CONF']
        devicetab = {k for k in deviceconfig.sections() if k not in conftab }
        #print(devicetab)
        for devicename in devicetab:
            self.createDevice(devicename)


    ###################################
    ## Auxiliary Configuration Methods
    ###################################
    def loadAuxConfigs(self):
        for auxconf, auxconffile in self.config['AUXCONF'].items():
            self.auxconf[auxconf] = {}
            auxconfig = configparser.ConfigParser()
            auxconfig.read(auxconffile)
            for aux in auxconfig.sections():
                self.auxconf[auxconf][aux] = {}
                for auxconfname in auxconfig.options(aux):
                    self.auxconf[auxconf][aux][auxconfname] = auxconfig[aux][auxconfname]

    def getAuxConfigs(self):
        return self.auxconf

    def createElement(self, elementcat, elementname):
        if self.debug == 1:
            print("#############################################")
            print("# {} {} Configuration : ".format(elementcat, elementname))
            print("#############################################")
            print("# {}".format(self.getAuxConfigs()[elementcat]['PROPERTIES']))
            print("# {}".format(self.getElementConfig(elementcat, elementname)))
            print("#############################################")
        argslist = []
        for propnum, propname in sorted(self.getAuxConfigs()[elementcat]['PROPERTIES'].items()):
            if self.debug == 1:
                print("# {} : {}".format(propnum, propname))
            if propname == 'device':
                argslist.append(self.getDevice(self.getElementConfig(elementcat, elementname)[propname]))
            else:
                argslist.append(self.getElementConfig(elementcat, elementname)[propname])
        if self.debug == 1:
            print("#\r")
        MOD = self.getModule(self.getAuxConfigs()[elementcat]['CONF']['module'])
        return MOD(*argslist)

    def createElementCat(self, elementcat):
        conftab = ['CONF', 'PROPERTIES']
        elementstab = {k for k in self.getElementCatConfig(elementcat) if k not in conftab }
        for element in elementstab:
            self.elements[element] = self.createElement(elementcat, element)
        return self.elements

    def createElements(self):
        if self.debug == 1:
            print("#############################################")
            print("# Creating All Elements ...")
            print("#############################################")
            print("\r")
        for elementcat in self.auxconf:
            self.createElementCat(elementcat)
            
    def getElementCatConfig(self, elementcat):
        return self.auxconf[elementcat]

    def getElementConfig(self, elementcat, elementname):
        return self.auxconf[elementcat][elementname]

    def getElements(self):
        return self.elements

    def getElement(self, elementname):
        return self.elements[elementname]
