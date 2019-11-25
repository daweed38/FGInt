#!/usr/bin/env python3

# System Module Import
import socket
import os
import sys
import logging
import socketserver
import operator
import time
import struct
import subprocess
import re

# Modules Import
from .FGIntI2C import I2CBus as I2CBus

########################################
# Class FGIntServer
# Create & Manage TCP Server to Comunicate
# with Flightgear
########################################

class FGIntDaemonHandler(socketserver.StreamRequestHandler):

    '''
    This Class define Handler that will
    respond to client request
    '''

    def handle(self):
        # Sending Banner
        self.banner = 'Welcome on FGInterface\r\n'
        self.wfile.write(self.banner.encode('utf-8'))
        self.loop = True
        self.I2CBus = I2CBus()

        while True:
           # Processing Request
           # Reading Command Sent
           self.data = self.rfile.readline().strip()
           rcvdata = self.data.decode('utf-8')

           # Sending Command as Acknowledgement
           if len(rcvdata) > 0:
               print("Receive Data : {}".format(rcvdata))
               #data = "Command Executed : " + rcvdata + "\r\n"
               #self.wfile.write(data.encode('utf-8'))

               rcvdatatab = rcvdata.split()
               if len(rcvdatatab) > 0:
                   cmd = rcvdatatab[0]
                   # Processing Request Command
                   if cmd == 'exit':
                       print("Exiting ....")
                       self.loop = False
                       break

                   elif cmd == 'help':
                       help_data = self.getHelp()
                       self.wfile.write(help_data.encode('utf-8'))

                   elif cmd == 'show':
                       if len(rcvdatatab) > 1:
                           show_data = self.showData(rcvdatatab[1])
                       else:
                           show_data = "Show Command not Reconized\r\n"
                       self.wfile.write(show_data.encode('utf-8'))

                   elif cmd == 'list':
                       list_data = str(type(rcvdatatab)) + "\r\n"
                       list_data = "Len : " + str(len(rcvdatatab)) + str(rcvdatatab) + "\r\n"
                       self.wfile.write(list_data.encode('utf-8'))

                   elif cmd == 'store':
                       if len(rcvdatatab) > 1:
                           store_data = "Storing Data " + str(rcvdatatab) + "\r\n"
                           self.wfile.write(store_data.encode('utf-8'))
                           self.storeData(rcvdatatab)
                       else:
                           store_data = "Store Command not Reconized\r\n"
                           self.wfile.write(store_data.encode('utf-8'))

                   else:
                       notreco = "Command Not Reconized : " + cmd + "\r\n"
                       self.wfile.write(notreco.encode('UTF-8'))

           if not self.data or self.loop == False: 
               print("Breaking process ...")
               break

    def showData(self, showcmd):
        if showcmd == 'piversion':
            show_data = "Rpi Version : " + str(I2CBus.getPiRevision())
        elif showcmd == 'busnumber':
            show_data = "Bus Number : " + str(I2CBus.getPiI2CBusNumber())
        elif showcmd == 'version':
            show_data = "FG Interface Server Version : " + str(self.getVersion())
        elif showcmd == 'devices':
            show_data = str(self.I2CBus.i2cdetect())
        else:
            show_data = 'Command not reconized'

        show_data = str(show_data) + "\r\n"
        return show_data

    def storeData(self, rcvdatatab):
        print("DATA  : {}".format(rcvdatatab))
        with open('Config/' + rcvdatatab[2] + '/devices.cfg', 'wb') as deviceconf:
            while True:
                self.data = self.rfile.readline().strip()
                stordata = self.data.decode('utf-8')
                if len(stordata) > 0:
                    if stordata == 'EOF':
                        print("Breaking Store process ...")
                        store_data = "No more data to Store ..."
                        self.wfile.write(store_data.encode('utf-8'))
                        break
                    print("Data To Store : {}".format(stordata))
                    deviceconf.write(self.data+b'\n')
        deviceconf.close()


    def getVersion(self):
        return "1.0"

    def getHelp(self):
        # Generating Help
        help_data = "Help :\r\n"
        help_data = help_data + " *help : display command help\r\n"
        help_data = help_data + " *list : list interface object(s). ie list <object>\r\n"
        help_data = help_data + " *show :\r\n"
        help_data = help_data + "        piversion : return Raspberry Version\r\n"
        help_data = help_data + "        busnumber : return I2C Bus Numer\r\n"
        help_data = help_data + "        version : return FG Int Server Version\r\n"
        help_data = help_data + "        devices : return devices detected Tab\r\n"
        return help_data

class FGIntDaemon:

    '''
    This Class define the FGInt Server
    '''

    def __init__(self, host, port):
        print("Server defined on host {} listning on port {}".format(host, port))
        self.host = host
        self.port = port
        self.fgintsrv = ''

    def createFGIntdSrv(self):
        socketserver.TCPServer.allow_reuse_address = True
        self.fgintsrv = socketserver.TCPServer((self.host, self.port), FGIntDaemonHandler)
        return self.fgintsrv
