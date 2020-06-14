#!/usr/bin/python3
import json
import time
import serial
import threading
import RPi.GPIO as GPIO
from Atlas import atlas_i2c
device = atlas_i2c(address=100,bus=1,file_path="/home/pi/rpi-aws_iot/ec100.json") 

ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5
)
counter=0
#ser.write(b't1.txt=\"test\"\xff\xff\xff')
#ser.write(b't0.bco=63488\xff\xff\xff')  


""" ser.write(b'get purge_button.val\xff\xff\xff')
x = ser.readline()
value = x[1:2]
print(value)  """

def purge_stop(timeout_seconds,pump_pin,sole_pin,ser):
  #GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
  #GPIO.output(pump_pin,0) # 0 signal value activates relay pin
  #time.sleep(int(timeout_seconds))
  GPIO.output(sole_pin,1)
  GPIO.output(pump_pin,1)
  ser.write(b'purge_button.val=0\xff\xff\xff')

def purge_cancel(pump_pin,sole_pin,ser):
  GPIO.output(sole_pin,1)
  GPIO.output(pump_pin,1)
  ser.write(b'purge_button.val=0\xff\xff\xff')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
sole_pin = 4
pump_pin = 17
timeout_seconds = 10
# Cada vez que el programa inicia hay que desactivar la purga
ser.write(b'purge_button.val=0\xff\xff\xff')
purgeOff = True
GPIO.setup(sole_pin,GPIO.OUT)
GPIO.setup(pump_pin,GPIO.OUT)
GPIO.output(sole_pin,1) # 1 desactiva el relay 
GPIO.output(pump_pin,1) 


timer = threading.Timer(timeout_seconds,purge_stop,args=(timeout_seconds,pump_pin,sole_pin,ser))

while 1:
    #ser.write(b't0.txt=\"test\"\xff\xff\xff')
    #ser.write(b'get t0.txt\xff\xff\xff')
    #ser.write(b'sendme\xff\xff\xff')
    
    try: 
      with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
        core_temp_json = json.load(f)
        f.close()
        #print(core_temp_json['CPUTemp'])
        #cputemp= 't2.txt=\"' + str(core_temp_json['CPUTemp']) + '\"\xff\xff\xff'
        ser.write(b't2.txt=\"' + str.encode(repr(core_temp_json['CPUTemp'])) + b'\"\xff\xff\xff')
        time.sleep(0.005)
    except Exception as e:
      print("!!! serial-read.py exception: ",repr(e))
      
    x = ser.readline()
    #print(type(x))
    #print(len(x))

    

    if (len(x) > 0):
      if (x[0:1] == b'e'):
        print("~~~ evento ~~~")
        if (x[2:3] == b'\x05'):
          print("purge button")
          ser.write(b'get purge_button.val\xff\xff\xff')
          x = ser.readline()
          value = x[1:2]
          if value == b'\x01':
            #thread_purge = threading.Thread(target=purge_start, args=(timeout_seconds,pump_pin,sole_pin,ser))
            #thread_purge.start()
            GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
            GPIO.output(pump_pin,0) # 0 signal value activates relay pin
            timer.start()
          elif value == b'\x00':
            #thread_purge_cancel = threading.Thread(target=purge_cancel, args=(pump_pin,sole_pin,ser))
            #thread_purge_cancel.start()
            #for th in threading.enumerate():
              #print(th.get_native_id())
              #th.do_run = False

            #current_thread = threading.currentThread()
            #current_thread.do_run = False
            timer.cancel()
            GPIO.output(sole_pin,1) # 1 desactiva el relay 
            GPIO.output(pump_pin,1) 
            ser.write(b'purge_button.val=0\xff\xff\xff')

        elif(x[2:3] == b'\x01'):
          print("read ec button")
          ec = device.query('r')
          print(repr(ec))
          ser.write(b't0.txt=\"'+str.encode(repr(ec))+b'\"\xff\xff\xff')
      #print(x[0:1])
      #print(x[2:3])
      print(x)
