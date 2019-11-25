#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Module Import
import socket
import os
import sys
import operator
import time
import struct
import hashlib

###################################
#
# Debug Mode :
# Level 0 : Debug mode off
# Level 1 : Debug mode on FGInt
# Level 2 : Debug mode on FG Int Device
# Level 3 : Debug mode on FG Int Object
# Level 4 : Debug mode on Bus I2C
# Level 5 : Debug mode on Object I2C
#
###################################

##############################
# Modules Import
##############################
from FGInterface import FGInterface as FGINT
from RotaryEncoder import EncoderWorker as WORKER

########################################
# Variables Initialisation
########################################
BOUNCETIME = 1000
BUFFERSIZE = 1024
FGINTADDR = '192.168.0.51'
FGINTPORT = 7800
FGADDR = '192.168.0.185'
FGPORT = 7850
loop = True
data_tree = {}
props_tree = {}
oldcypher = ''

########################################
########################################
# Main Interface Construction
########################################
########################################

########################################
# Interface Creation
########################################
# Interface INT1 Creation (using int1.cfg configuration file)
# Configuration file is read & store in memory
INT1 = FGINT('radiopanel.cfg')
