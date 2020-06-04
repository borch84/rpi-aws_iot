#!/usr/bin/python3
import time
import serial
from Atlas import atlas_i2c
device = atlas_i2c(address=100,bus=1,file_path="/home/pi/rpi-aws_iot/ec100.json") 

ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)
counter=0
ser.write(b't1.txt=\"test\"\xff\xff\xff')
ser.write(b't0.bco=63488\xff\xff\xff')
while 1:
    #ser.write(b't0.txt=\"test\"\xff\xff\xff')
    #ser.write(b'get t0.txt\xff\xff\xff')
    #ser.write(b'sendme\xff\xff\xff')
    x = ser.readline()
    #print(type(x))
    #print(len(x))
    if (len(x) > 0):
      if (x[0:1] == b'e'):
        print("~~~ evento ~~~")
        if (x[2:3] == b'\x0b'):
          print("purge button")
        elif(x[2:3] == b'\x08'):
          print("lights button")
        elif(x[2:3] == b'\x01'):
          print("read ec button")
          ec = device.query('r')
          print(repr(ec))
          ser.write(b't0.txt=\"'+str.encode(repr(ec))+b'\"\xff\xff\xff')
      #print(x[0:1])
      #print(x[2:3])
      print(x)
