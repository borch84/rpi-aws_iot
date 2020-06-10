#!/usr/bin/python3
import json
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
#ser.write(b't1.txt=\"test\"\xff\xff\xff')
#ser.write(b't0.bco=63488\xff\xff\xff')  



while 1:
    #ser.write(b't0.txt=\"test\"\xff\xff\xff')
    #ser.write(b'get t0.txt\xff\xff\xff')
    #ser.write(b'sendme\xff\xff\xff')
    
    with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
      core_temp_json = json.load(f)
      f.close()
      print(core_temp_json['CPUTemp'])
      #cputemp= 't2.txt=\"' + str(core_temp_json['CPUTemp']) + '\"\xff\xff\xff'
      ser.write(b't2.txt=\"' + str.encode(repr(core_temp_json['CPUTemp'])) + b'\"\xff\xff\xff')
      time.sleep(0.005)
      
      
    x = ser.readline()
    #print(type(x))
    #print(len(x))
    if (len(x) > 0):
      if (x[0:1] == b'e'):
        print("~~~ evento ~~~")
        if (x[2:3] == b'\x05'):
          print("purge button")
        elif(x[2:3] == b'\x01'):
          print("read ec button")
          ec = device.query('r')
          print(repr(ec))
          ser.write(b't0.txt=\"'+str.encode(repr(ec))+b'\"\xff\xff\xff')
      #print(x[0:1])
      #print(x[2:3])
      print(x)
