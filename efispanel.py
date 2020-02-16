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
BOUNCETIME = 1500
BUFFERSIZE = 1024
FGINTADDR = '192.168.0.51'
FGINTPORT = 7700
FGADDR = '192.168.0.150'
FGPORT = 7750
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
INT1 = FGINT('efispanel.cfg', 0)
INT1.createDevices()
INT1.createElements()

########################################
# LEDPACK1
########################################
LEDPACK1 = INT1.getDevice('LEDPACK1')
LEDPACK1.configMCP(1)
LEDPACK1.Start()

INHGDSP1=INT1.getElement('INHGDSP1')
HPADSP1=INT1.getElement('HPADSP1')
INHGDSP2=INT1.getElement('INHGDSP2')
HPADSP2=INT1.getElement('HPADSP2')

########################################
# IOPACK1
########################################
IOPACK1 = INT1.getDevice('IOPACK1')
IOPACK1.configMCP(1)

########################################
# IOPACK2
########################################
IOPACK2 = INT1.getDevice('IOPACK2')
IOPACK2.configMCP(1)

########################################
# IOPACK3
########################################
IOPACK3 = INT1.getDevice('IOPACK3')
IOPACK3.configMCP(1)
data_tree['efis0stdsw'] = 0
data_tree['efis0fdsw'] = 0
data_tree['efis0ilssw'] = 0
data_tree['efis0mode'] = 0


########################################
# IOPACK4
########################################
IOPACK4 = INT1.getDevice('IOPACK4')
IOPACK4.configMCP(1)
data_tree['efis0adfvor1'] = 'off'
data_tree['efis0adfvor2'] = 'off'
data_tree['efis0rose'] = INT1.getElement('EFIS0ROSERSW').getSwitchState()
data_tree['efis0zoom'] = INT1.getElement('EFIS0ZOOMRSW').getSwitchState()


########################################
# Objects Creation
########################################
#INT1.createElements()

QNHCPTENC = WORKER(INT1.getElement('QNHCPTENC'))
QNHCPTENC.start()
data_tree['qnhdata'] = QNHCPTENC.getValue()
data_tree['qnhdatadir'] = ''

# print(INT1.getConfig())
# print(INT1.getAuxConfigs())

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

    data = connection.recv(BUFFERSIZE).strip().decode('utf-8')
    if data != '':
        for props in data.split(':'):
            props_tree[props.split('=')[0]] = props.split('=')[1]

    try:
        print('connection from', client_address)
        while loop == True:
            data = connection.recv(BUFFERSIZE).strip().decode('utf-8')
            if data != '':
                #print(data)
                for props in data.split(':'):
                    props_tree[props.split('=')[0]] = props.split('=')[1]

            if int(props_tree['fmgcinit']) != 1:
                continue

            if float(props_tree['dc-ess']) > 25:
                HPADSP1.setStatus('ON')
                HPADSP2.setStatus('ON')
                LEDPACK1.Start()
            else:
                HPADSP1.setStatus('OFF')
                HPADSP2.setStatus('OFF')
                LEDPACK1.Stop()

            ########################################
            # Key Switch Management
            ########################################
            if float(props_tree['dc-ess']) > 25:
                if INT1.getElement('EFIS0STDSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0STDSW').getInputState() == 1:
                    data_tree['efis0stdsw'] = 1
                else:
                    data_tree['efis0stdsw'] = 0

                if INT1.getElement('EFIS0FDSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0FDSW').getInputState() == 1:
                    data_tree['efis0fdsw'] = 1
                else:
                    data_tree['efis0fdsw'] = 0

                if INT1.getElement('EFIS0ILSSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0ILSSW').getInputState() == 1:
                    data_tree['efis0ilssw'] = 1
                else:
                    data_tree['efis0ilssw'] = 0
                
                if INT1.getElement('EFIS0CSTRSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0CSTRSW').getInputState() == 1:
                    data_tree['efis0mode'] = 'cstr'
                elif INT1.getElement('EFIS0WPTSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0WPTSW').getInputState() == 1:
                    data_tree['efis0mode'] = 'wpt'
                elif INT1.getElement('EFIS0VORDSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0VORDSW').getInputState() == 1:
                    data_tree['efis0mode'] = 'vord'
                elif INT1.getElement('EFIS0NDBSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0NDBSW').getInputState() == 1:
                    data_tree['efis0mode'] = 'ndb'
                elif INT1.getElement('EFIS0ARPTSW').getMillis() > BOUNCETIME and INT1.getElement('EFIS0ARPTSW').getInputState() == 1:
                    data_tree['efis0mode'] = 'arpt'
                else:
                    data_tree['efis0mode'] = 0

            ########################################
            # VOR / ADF Switch Management
            ########################################
            data_tree['efis0adfvor1'] = INT1.getElement('EFIS0ADFVOR1SW').getSwitchState()
            data_tree['efis0adfvor2'] = INT1.getElement('EFIS0ADFVOR2SW').getSwitchState()

            ########################################
            # Rotary Switch Management
            ########################################
            data_tree['efis0rose'] = INT1.getElement('EFIS0ROSERSW').getSwitchState()
            data_tree['efis0zoom'] = INT1.getElement('EFIS0ZOOMRSW').getSwitchState()

            ########################################
            # Display Value Management
            ########################################
            if int(props_tree['annun-test']) != 1:
                if int(props_tree['efis0_std']) == 1:
                    HPADSP1.writeDisplay(' Std', 0)
                    HPADSP2.writeDisplay(' Std', 0)
                else:
                    HPADSP1.writeDisplay(props_tree['efis0_hpa'], 0)
                    HPADSP2.writeDisplay(props_tree['efis0_hpa'], 0)
            else:
                HPADSP1.writeDisplay(str('8888'), 0)
                HPADSP2.writeDisplay(str('8888'), 0)
                

            delta = QNHCPTENC.get_delta()
            if delta != 0:
                if delta > 0:
                    data_tree['qnhdata'] = int(data_tree['qnhdata']) + int(QNHCPTENC.getIncrement())
                    data_tree['qnhdatadir'] = 'incr'
                else:
                    data_tree['qnhdata'] = int(data_tree['qnhdata']) - int(QNHCPTENC.getIncrement())
                    data_tree['qnhdatadir'] = 'decr'
                if data_tree['qnhdata'] > int(QNHCPTENC.getMaxValue()):
                    data_tree['qnhdata'] = int(QNHCPTENC.getMaxValue())
                if data_tree['qnhdata'] < int(QNHCPTENC.getMinValue()):
                    data_tree['qnhdata'] = int(QNHCPTENC.getMinValue())
            else:
                data_tree['qnhdatadir'] = ''

            ########################################
            # Switchs Lights Management
            ########################################
            if int(props_tree['annun-test']) != 1:
                if int(props_tree['efis0_fd']) == 1:
                    INT1.getElement('EFIS0FDSWL').setLightState('ON')
                else:
                    INT1.getElement('EFIS0FDSWL').setLightState('OFF')
                
                if int(props_tree['efis0_ils']) == 1:
                    INT1.getElement('EFIS0ILSSWL').setLightState('ON')
                else:
                    INT1.getElement('EFIS0ILSSWL').setLightState('OFF')
                
                if int(props_tree['efis0_cstr']) == 1:
                    INT1.getElement('EFIS0CSTRSWL').setLightState('ON')
                else:
                    INT1.getElement('EFIS0CSTRSWL').setLightState('OFF')
                
                if int(props_tree['efis0_wpt']) == 1:
                    INT1.getElement('EFIS0WPTSWL').setLightState('ON')
                else:
                    INT1.getElement('EFIS0WPTSWL').setLightState('OFF')
                
                if int(props_tree['efis0_vord']) == 1:
                    INT1.getElement('EFIS0VORDSWL').setLightState('ON')
                else:
                    INT1.getElement('EFIS0VORDSWL').setLightState('OFF')
                
                if int(props_tree['efis0_ndb']) == 1:
                    INT1.getElement('EFIS0NDBSWL').setLightState('ON')
                else:
                    INT1.getElement('EFIS0NDBSWL').setLightState('OFF')
                
                if int(props_tree['efis0_arpt']) == 1:
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

            ########################################
            # DATA MANAGEMENT
            ########################################
            datastr = str(data_tree['qnhdata'])
            datastr = datastr + ':' + str(data_tree['efis0stdsw'])
            datastr = datastr + ':' + str(data_tree['efis0fdsw'])
            datastr = datastr + ':' + str(data_tree['efis0ilssw'])
            datastr = datastr + ':' + str(data_tree['efis0mode'])
            datastr = datastr + ':' + str(data_tree['efis0adfvor1'])
            datastr = datastr + ':' + str(data_tree['efis0adfvor2'])
            datastr = datastr + ':' + str(data_tree['efis0rose'])
            datastr = datastr + ':' + str(data_tree['efis0zoom'])


            ########################################
            # DATA SENDING PROCESS
            ########################################
            cypher = hashlib.md5(datastr.encode('utf-8')).digest()
            if cypher != oldcypher:
                print("DATA : {} | PROPS : {}".format(datastr, props_tree))
                sockclient.send(bytes(datastr, 'utf-8'))
                sockclient.send(bytes("\n", 'utf8'))
                oldcypher = cypher

            # Time Loop Standby
            # to not eat all resources
            #time.sleep(0.01)

    finally:
        # Clean up the connection
        connection.close()
        sockclient.close()
        sock.close()

