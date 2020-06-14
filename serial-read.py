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

e = threading.Event()
doRun = False

def purge_start(timeout_seconds,pump_pin,sole_pin,ser):
  #global doRun
  while True:
    print("Thread esperando hasta que usuario active boton de purga")
    e.wait()
    GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
    GPIO.output(pump_pin,0) # 0 signal value activates relay pin
    #time.sleep(int(timeout_seconds))
    #GPIO.output(sole_pin,1)
    #GPIO.output(pump_pin,1)
    #ser.write(b'purge_button.val=0\xff\xff\xff')

def purge_timer(pump_pin,sole_pin,ser):
    #global doRun
    #doRun = False

    #e.wait()
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
timeout_seconds = 5
# Cada vez que el programa inicia hay que desactivar la purga
ser.write(b'purge_button.val=0\xff\xff\xff')
purgeOff = True
GPIO.setup(sole_pin,GPIO.OUT)
GPIO.setup(pump_pin,GPIO.OUT)
GPIO.output(sole_pin,1) # 1 desactiva el relay 
GPIO.output(pump_pin,1) 


#timer = threading.Timer(timeout_seconds,purge_timer,args=(pump_pin,sole_pin,ser))

thread_purge = threading.Thread(target=purge_start, args=(timeout_seconds,pump_pin,sole_pin,ser))
thread_purge.start()

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
        #time.sleep(0.005)
    except Exception as e:
      print("!!! serial-read.py exception: ",repr(e))
      
    
    x = ser.readline()
    #print(type(x))
    #print(len(x))
    timer = threading.Timer(timeout_seconds,purge_timer,args=(pump_pin,sole_pin,ser))    
    

    if (len(x) > 0):
      if (x[0:1] == b'e'):
        print("~~~ evento ~~~")
        if (x[2:3] == b'\x05'):
          print("purge button")
          ser.write(b'get purge_button.val\xff\xff\xff')
          x = ser.readline()
          value = x[1:2]
          if value == b'\x01':
            #Activa el boton. 
            #current_thread = threading.current_thread()
            #if not current_thread.is_alive():
            #if not doRun: 
            #  doRun = True
            #  timer.start()
            #if threading.enumerate() == 1:
            GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
            GPIO.output(pump_pin,0) # 0 signal value activates relay pin
            timer.start()
            #e.set()
            #e.clear()
            #thread_purge.join()
          elif value == b'\x00':
            #Apaga el boton.
            #thread_purge_cancel = threading.Thread(target=purge_cancel, args=(pump_pin,sole_pin,ser))
            #thread_purge_cancel.start()
            #for th in threading.enumerate():
              #print(th.get_native_id())
              #th.cancel()

            #current_thread = threading.currentThread()
            #current_thread.do_run = False
            #if current_thread.is_alive():
          
            #if doRun:
            #  doRun = False
            #  timer.cancel()
            
            GPIO.output(sole_pin,1) # 1 desactiva el relay 
            GPIO.output(pump_pin,1) 
            ser.write(b'purge_button.val=0\xff\xff\xff')
            timer.cancel()
            #e.wait()


        elif(x[2:3] == b'\x01'):
          print("read ec button")
          ec = device.query('r')
          print(repr(ec))
          ser.write(b't0.txt=\"'+str.encode(repr(ec))+b'\"\xff\xff\xff')
      #print(x[0:1])
      #print(x[2:3])
      print(x)
