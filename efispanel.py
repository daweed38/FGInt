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
FGADDR = '192.168.0.150'
FGPORT = 7850
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
INT1 = FGINT('efispanel.cfg')

LEDPACK1 = INT1.getDevice('LEDPACK1')
IOPACK1 = INT1.getDevice('IOPACK1')
IOPACK2 = INT1.getDevice('IOPACK2')
IOPACK3 = INT1.getDevice('IOPACK3')
IOPACK4 = INT1.getDevice('IOPACK4')

########################################
# Create ALL Elements
########################################
INT1.createElements()

########################################
# LEDPACK1
########################################
LEDPACK1.configMCP(1)

QNHCPTDSP = INT1.getElement('QNHCPTDSP')
QNHFODSP = INT1.getElement('QNHFODSP')

EFIS0FDSWL = INT1.getElement('EFIS0FDSWL')
EFIS0ILSSWL = INT1.getElement('EFIS0ILSSWL')
EFIS0CSTRSWL = INT1.getElement('EFIS0CSTRSWL')
EFIS0WPTSWL = INT1.getElement('EFIS0WPTSWL')
EFIS0VORDSWL = INT1.getElement('EFIS0VORDSWL')
EFIS0NDBSWL = INT1.getElement('EFIS0NDBSWL')
EFIS0ARPTSWL = INT1.getElement('EFIS0ARPTSWL')

########################################
# IOPACK1
########################################
IOPACK1.configMCP(1)

########################################
# IOPACK2
########################################
IOPACK2.configMCP(1)

QNHCPTENC = WORKER(INT1.getElement('QNHCPTENC'))
QNHCPTENC.start()
cptqnhencdata = QNHCPTENC.getValue()

########################################
# IOPACK3
########################################
IOPACK3.configMCP(1)

EFIS0STDSW = INT1.getElement('EFIS0STDSW')
EFIS0FDSW = INT1.getElement('EFIS0FDSW')
EFIS0ILSSW = INT1.getElement('EFIS0ILSSW')
EFIS0CSTRSW = INT1.getElement('EFIS0CSTRSW')
EFIS0WPTSW = INT1.getElement('EFIS0WPTSW')
EFIS0VORDSW = INT1.getElement('EFIS0VORDSW')
EFIS0NDBSW = INT1.getElement('EFIS0NDBSW')
EFIS0ARPTSW  = INT1.getElement('EFIS0ARPTSW')

########################################
# IOPACK4
########################################
IOPACK4.configMCP(1)

EFIS0ADFVOR1SW = INT1.getElement('EFIS0ADFVOR1SW')
EFIS0ADFVOR2SW = INT1.getElement('EFIS0ADFVOR2SW')
EFIS0ROSERSW = INT1.getElement('EFIS0ROSERSW')
EFIS0ZOOMRSW = INT1.getElement('EFIS0ZOOMRSW')

########################################
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
                QNHCPTDSP.setStatus('ON')
                QNHFODSP.setStatus('ON')
            else:
                LEDPACK1.Stop()
                QNHCPTDSP.setStatus('OFF')
                QNHFODSP.setStatus('OFF')

            ########################################
            # Display Management
            ########################################
            if float(props_tree['dc-ess']) > 25:
                if int(props_tree['annun-test']) != 1:
                    # QNH Cpt
                    if int(props_tree['efis0-std']) == 1:
                        QNHCPTDSP.writeDisplay(' Std', 0)
                    else:
                        if int(props_tree['efis0-mode']) == 1:
                            QNHCPTDSP.writeDisplay(str(props_tree['efis0-inhg'].replace('.','')), 1)
                        else:
                            QNHCPTDSP.writeDisplay(str(props_tree['efis0-hpa']), 0)

                    # QNH Fo
                    if int(props_tree['efis0-std']) == 1:
                        QNHFODSP.writeDisplay(' Std', 0)
                    else:
                        if int(props_tree['efis0-mode']) == 1:
                            QNHFODSP.writeDisplay(str(props_tree['efis0-inhg'].replace('.','')), 1)
                        else:
                            QNHFODSP.writeDisplay(str(props_tree['efis0-hpa']), 0)
                else:
                    QNHCPTDSP.writeDisplay(str('8888'), 0)
                    QNHFODSP.writeDisplay(str('8888'), 0)

            ##### ##### ##### ##### #####
            # Light Indicator Management
            ##### ##### ##### ##### #####
            if float(props_tree['dc-ess']) > 25:
                if int(props_tree['annun-test']) != 1:
                    if int(props_tree['efis0-fd']) == 1:
                        INT1.getElement('EFIS0FDSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0FDSWL').setLightState('OFF')

                    if int(props_tree['efis0-ils']) == 1:
                        INT1.getElement('EFIS0ILSSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0ILSSWL').setLightState('OFF')

                    if int(props_tree['efis0-cstr']) == 1:
                        INT1.getElement('EFIS0CSTRSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0CSTRSWL').setLightState('OFF')

                    if int(props_tree['efis0-wpt']) == 1:
                        INT1.getElement('EFIS0WPTSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0WPTSWL').setLightState('OFF')

                    if int(props_tree['efis0-vord']) == 1:
                        INT1.getElement('EFIS0VORDSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0VORDSWL').setLightState('OFF')

                    if int(props_tree['efis0-ndb']) == 1:
                        INT1.getElement('EFIS0NDBSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0NDBSWL').setLightState('OFF')

                    if int(props_tree['efis0-arpt']) == 1:
                        INT1.getElement('EFIS0ARPTSWL').setLightState('ON')
                    else:
                        INT1.getElement('EFIS0ARPTSWL').setLightState('OFF')
                else:
                    INT1.getElement('EFIS0FDSWL').setLightState('ON')
                    INT1.getElement('EFIS0ILSSWL').setLightState('ON')
                    INT1.getElement('EFIS0CSTRSWL').setLightState('ON')
                    INT1.getElement('EFIS0WPTSWL').setLightState('ON')
                    INT1.getElement('EFIS0VORDSWL').setLightState('ON')
                    INT1.getElement('EFIS0NDBSWL').setLightState('ON')
                    INT1.getElement('EFIS0ARPTSWL').setLightState('ON')

            ##### ##### ##### ##### #####
            # Encoder Management
            ##### ##### ##### ##### #####
            delta = QNHCPTENC.get_delta()
            if delta != 0:
                if delta > 0:
                    cptqnhencdata = int(cptqnhencdata) + int(QNHCPTENC.getIncrement())
                    cptqnhencdir = 'incr'
                else:
                    cptqnhencdata = int(cptqnhencdata) - int(QNHCPTENC.getIncrement())
                    cptqnhencdir = 'decr'

                if cptqnhencdata > int(QNHCPTENC.getMaxValue()):
                    cptqnhencdata = int(QNHCPTENC.getMinValue())
                if cptqnhencdata < int(QNHCPTENC.getMinValue()):
                    cptqnhencdata = int(QNHCPTENC.getMaxValue())
            else:
                cptqnhencdir = ''

            input_tree['QNHCPTENC'] = cptqnhencdata
            input_tree['QNHCPTENCDIR'] = cptqnhencdir

            ########################################
            # Toggle Switch Management
            ########################################

            if EFIS0STDSW.getMillis() > BOUNCETIME and int(EFIS0STDSW.getInputState()) == 1:
                input_tree['EFIS0STDSW'] = 1
            else:
                input_tree['EFIS0STDSW'] = 0

            '''
            EFIS0STDSW = INT1.getElement('EFIS0STDSW')
            EFIS0FDSW = INT1.getElement('EFIS0FDSW')
            EFIS0ILSSW = INT1.getElement('EFIS0ILSSW')
            EFIS0CSTRSW = INT1.getElement('EFIS0CSTRSW')
            EFIS0WPTSW = INT1.getElement('EFIS0WPTSW')
            EFIS0VORDSW = INT1.getElement('EFIS0VORDSW')
            EFIS0NDBSW = INT1.getElement('EFIS0NDBSW')
            EFIS0ARPTSW  = INT1.getElement('EFIS0ARPTSW')
            '''

            if EFIS0FDSW.getMillis() > BOUNCETIME and int(EFIS0FDSW.getInputState()) == 1:
                input_tree['EFIS0FDSW'] = 1
            else:
                input_tree['EFIS0FDSW'] = 0

            if EFIS0ILSSW.getMillis() > BOUNCETIME and int(EFIS0ILSSW.getInputState()) == 1:
                input_tree['EFIS0ILSSW'] = 1
            else:
                input_tree['EFIS0ILSSW'] = 0

            if EFIS0CSTRSW.getMillis() > BOUNCETIME and int(EFIS0CSTRSW.getInputState()) == 1:
                input_tree['EFIS0MODE'] = 'cstr'

            elif EFIS0WPTSW.getMillis() > BOUNCETIME and int(EFIS0WPTSW.getInputState()) == 1:
                input_tree['EFIS0MODE'] = 'wpt'

            elif EFIS0VORDSW.getMillis() > BOUNCETIME and int(EFIS0VORDSW.getInputState()) == 1:
                input_tree['EFIS0MODE'] = 'vord'

            elif EFIS0NDBSW.getMillis() > BOUNCETIME and int(EFIS0NDBSW.getInputState()) == 1:
                input_tree['EFIS0MODE'] = 'ndb'

            elif EFIS0ARPTSW.getMillis() > BOUNCETIME and int(EFIS0ARPTSW.getInputState()) == 1:
                input_tree['EFIS0MODE'] = 'arpt'
            else:
                input_tree['EFIS0MODE'] = 0

            ########################################
            # VOR / ADF Switch Management
            ########################################
            input_tree['EFIS0ADFVOR1SW'] = EFIS0ADFVOR1SW.getSwitchState()
            input_tree['EFIS0ADFVOR2SW'] = EFIS0ADFVOR2SW.getSwitchState()

            ########################################
            # Rotary Switch Management
            ########################################
            input_tree['EFIS0ROSERSW'] = EFIS0ROSERSW.getSwitchState()
            input_tree['EFIS0ZOOMRSW'] = EFIS0ZOOMRSW.getSwitchState()

            ########################################
            # DATA MANAGEMENT
            ########################################

            datastr = str(input_tree['QNHCPTENC'])
            datastr = datastr + ':' + str(input_tree['QNHCPTENCDIR'])
            datastr = datastr + ':' + str(input_tree['EFIS0STDSW'])
            datastr = datastr + ':' + str(input_tree['EFIS0FDSW'])
            datastr = datastr + ':' + str(input_tree['EFIS0ILSSW'])
            datastr = datastr + ':' + str(input_tree['EFIS0MODE'])
            datastr = datastr + ':' + str(input_tree['EFIS0ADFVOR1SW'])
            datastr = datastr + ':' + str(input_tree['EFIS0ADFVOR2SW'])
            datastr = datastr + ':' + str(input_tree['EFIS0ROSERSW'])
            datastr = datastr + ':' + str(input_tree['EFIS0ZOOMRSW'])

            ########################################
            # DATA SENDING PROCESS
            ########################################
            cypher = hashlib.md5(datastr.encode('utf-8')).digest()
            if cypher != oldcypher:
                print("DATA : {} | PROPS : {}".format(datastr, props_tree))
                sockclient.send(bytes(datastr, 'utf-8'))
                sockclient.send(bytes("\n", 'utf8'))
                oldcypher = cypher
    finally:
        # Clean up device
        LEDPACK1.Stop()
        LEDPACK1.configMCP(0)
        IOPACK1.configMCP(0)
        IOPACK2.configMCP(0)
        IOPACK3.configMCP(0)
        IOPACK4.configMCP(0)
        # Clean up the connection
        connection.close()
        sockclient.close()
        sock.close()
