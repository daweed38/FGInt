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
from _thread import *

# Modules Import
from FGIntMngtd.FGIntDaemon import FGIntDaemon as FGIntD

host = '192.168.0.51'
#host = '10.16.135.58'
port = 9900

fgintd = FGIntD(host, port)
fgintd_srv = fgintd.createFGIntdSrv()

print(fgintd_srv)

try:
    print("Starting Server")
    fgintd_srv.serve_forever()
except KeyboardInterrupt:
    fgintd_srv.shutdown()
