#!/usr/bin/env python3

from urllib.request import urlopen
import urllib.error
import socket

#TODO: no muestra si se conecta internet!

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	sock.connect(('https://a3s9lktlbmjbgn-ats.iot.us-east-1.amazonaws.com/things/yUp3qLUftKGGY01XdcL5/shadow',8443))
except socket.error as e:
	print('Excepcion: '+repr(e))


try:
    urlopen("https://a3s9lktlbmjbgn-ats.iot.us-east-1.amazonaws.com/things/yUp3qLUftKGGY01XdcL5/shadow")
    #socket.create_connection("www.google.com", 80)
    print("**** CONECTADO A INTERNET! ****")
except urllib.error.URLError as e: 
    print("**** SIN CONEXION A INTERNET! ****")
    print(e.reason)
