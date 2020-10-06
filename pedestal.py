#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Module Import
import socket
import os
import sys
import re
import operator
import time
import struct
import hashlib
import datetime

import RPi.GPIO as GPIO

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

########################################
# Variables Initialisation
########################################
BOUNCETIME = 1500
BUFFERSIZE = 1024
FGINTADDR = '192.168.0.62'
FGINTPORT = 7700
FGADDR = '192.168.0.150'
FGPORT = 7750
loop = True
data_tree = {}
props_tree = {}
input_tree = {}
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
INT1 = FGINT('pedestal.cfg')

LEDPACK1 = INT1.getDevice('LEDPACK1')
IOPACK3 = INT1.getDevice('IOPACK3')

#print("Liste des Modules :")
#print(INT1.listModules())
#print("\r")
#print("Liste des Modules Chargés :")
#print(INT1.listLoadedModules())
#print("\r")
#print("Liste des Devices :")
#print(INT1.getDevices())
#print("\r")
#print("Configuration Auxiliaire")
#print(INT1.getAuxConfigs())
#print("\r")

########################################
# Elements Creation
########################################
#INT1.createElement('displays','XPNDRDSP')
#INT1.createElement('keypads','XPNDRPAD')
INT1.createElements()

########################################
# LEDPACK1
########################################
LEDPACK1.configMCP(1)
XPNDRDSP = INT1.getElement('XPNDRDSP')
XPNDRPAD = INT1.getElement('XPNDRPAD')

#print(XPNDRPAD.getMatrix())

input_tree['XPNDRPAD'] = XPNDRPAD.getKey()

########################################
# IOPACK3
########################################
IOPACK3.configMCP(1)

ATCIDENTSW = INT1.getElement('ATCIDENTSW')
ATCMODESW = INT1.getElement('ATCMODESW')

#######################################
# TCP Server Creation
########################################
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (FGINTADDR, FGINTPORT)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

########################################
# Main Loop
########################################

while loop == True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()

    sockclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockclient.connect((FGADDR, FGPORT))

    try:
        print('connection from', client_address)
        while loop == True:

            data = connection.recv(BUFFERSIZE).decode('utf-8')

            if data != '':
                #print(data)
                for props in data.replace('\n','').split(':'):
                    try:
                        props_tree[props.split('=')[0]] = props.split('=')[1]
                    except:
                        print(props)

            if int(props_tree['fmgcinit']) != 1:
                continue

            #print(props_tree)

            ########################################
            # Power Management
            ########################################

            if float(props_tree['dc-ess']) > 25:
                LEDPACK1.Start()
                #XPNDRDSP.setStatus('ON')
            else:
                LEDPACK1.Stop()
                #XPNDRDSP.setStatus('OFF')

            ########################################
            # Display Management
            ########################################
            if float(props_tree['dc-ess']) > 25:
                if int(props_tree['annun-test']) != 1:
                    # XPNDR DSP
                    if int(props_tree['atc-code']) != 0:
                        XPNDRDSP.setStatus('ON')
                        XPNDRDSP.writeDisplay(str(props_tree['atc-code']), 0)
                    else:
                        XPNDRDSP.setStatus('OFF')
                else:
                    XPNDRDSP.setStatus('ON')
                    XPNDRDSP.writeDisplay(str('8888'), 0)

            ########################################
            # Toggle Switch Management
            ########################################

            if ATCIDENTSW.getMillis() > BOUNCETIME and int(ATCIDENTSW.getInputState()) == 1:
                input_tree['ATCIDENTSW'] = 1
            else:
                input_tree['ATCIDENTSW'] = 0

            ########################################
            # Rotary Binanry Switch Management
            ########################################
            input_tree['ATCMODESW'] = ATCMODESW.getSwitchState()

            ########################################
            # Keypad Management
            ########################################
            #if XPNDRPAD.getKeyPressed() != 0:
            input_tree['XPNDRPAD'] = XPNDRPAD.getKey()

            ########################################
            # DATA MANAGEMENT
            ########################################

            datastr = str(input_tree['ATCIDENTSW'])
            datastr = datastr + ':' + str(input_tree['ATCMODESW'])
            datastr = datastr + ':' + str(input_tree['XPNDRPAD'])
            

            ########################################
            # DATA SENDING PROCESS
            ########################################
            cypher = hashlib.md5(datastr.encode('utf-8')).digest()
            if cypher != oldcypher:
                print("DATA : {} | PROPS : {}".format(datastr, props_tree))
                sockclient.send(bytes(datastr, 'utf-8'))
                sockclient.send(bytes("\n", 'utf8'))
                oldcypher = cypher


            #time.sleep(0.2)

    finally:
        # Clean up device
        LEDPACK1.Stop()
        LEDPACK1.configMCP(0)
        #IOPACK1.configMCP(0)
        #IOPACK2.configMCP(0)
        IOPACK3.configMCP(0)
        #IOPACK4.configMCP(0)
        # Clean up the connection
        connection.close()
        sockclient.close()
        sock.close()


