#!/usr/bin/python3
import json
import time
import serial
import threading
import RPi.GPIO as GPIO
from Atlas import atlas_i2c
import time_purge_handler_file

device = atlas_i2c(address=99,bus=1,file_path="/home/pi/aws_iot/ph99.json",sensor_type="ph")
 
ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5
)

def purge_timer(pump_pin,sole_pin,ser):
    GPIO.output(sole_pin,1)
    GPIO.output(pump_pin,1)
    ser.write(b'water_button.val=0\xff\xff\xff')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
sole_pin = 4
pump_pin = 17
timeout_seconds = 1
# Cada vez que el programa inicia hay que desactivar la purga
ser.write(b'water_button.val=0\xff\xff\xff')
#purgeOff = True
GPIO.setup(sole_pin,GPIO.OUT)
GPIO.setup(pump_pin,GPIO.OUT)
GPIO.output(sole_pin,1) # 1 desactiva el relay 
GPIO.output(pump_pin,1) 


minute_value = 0

minute_value = time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/purge_time.json')
ser.write(b'minuto_purga.txt=\"'+str.encode(repr(minute_value))+b'\"\xff\xff\xff')

while 1:

    try: 
      with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
        core_temp_json = json.load(f)
        f.close()
        #print(core_temp_json['CPUTemp'])
        ser.write(b't2.txt=\"' + str.encode(repr(core_temp_json['CPUTemp'])) + b'C\"\xff\xff\xff')
    except Exception as e:
      print("!!! read rpi cpu core log file exception: ",repr(e))

    try: 
      with open('/home/pi/aws_iot/sht31d.json','r') as f:
        sht31d_json = json.load(f)
        f.close()
        ser.write(b't5.txt=\"' + str.encode(repr(sht31d_json['t'])) + b'C\"\xff\xff\xff')
        ser.write(b't7.txt=\"' + str.encode(repr(sht31d_json['h'])) + b'%\"\xff\xff\xff')
    except Exception as e:
      print("!!! read sht31d.log file exception: ",repr(e))
    
    try: 
      with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
        core_temp_json = json.load(f)
        f.close()
        #print(core_temp_json['CPUTemp'])
        ser.write(b't2.txt=\"' + str.encode(repr(core_temp_json['CPUTemp'])) + b'C\"\xff\xff\xff')
    except Exception as e:
      print("!!! read rpi cpu core log file exception: ",repr(e))
    
    try:
      with open('/home/pi/aws_iot/ph99.json','r') as f:
        ph99_json = json.load(f)
        f.close()
        ser.write(b't0.txt=\"'+str.encode(repr(ph99_json['ph']))+b'ph\"\xff\xff\xff')
    except Exception as e:
      print("!!! read ph99.json file exception: ",repr(e))


    x = ser.readline()
    timer = threading.Timer(minute_value*timeout_seconds,purge_timer,args=(pump_pin,sole_pin,ser))    
    

    if (len(x) > 0):
      if (x[0:1] == b'e'):
        print("~~~ evento ~~~")
        if (x[2:3] == b'\x05'):
          print("water button")
          ser.write(b'get water_button.val\xff\xff\xff')
          x = ser.readline()
          value = x[1:2]
          if value == b'\x01':
            GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
            GPIO.output(pump_pin,0) # 0 signal value activates relay pin
            timer.start()

          elif value == b'\x00':
            GPIO.output(sole_pin,1) # 1 desactiva el relay 
            GPIO.output(pump_pin,1) 
            ser.write(b'water_button.val=0\xff\xff\xff')
            timer.cancel()


        elif(x[2:3] == b'\x01'):
          print("read ph button")
          ph = device.query('r')
          print(repr(ph))
          ser.write(b't0.txt=\"'+str.encode(repr(ph))+b'ph\"\xff\xff\xff')
        
        elif(x[2:3] == b'\x07'):
          print("minus button")
          if minute_value > 1:
            minute_value -= 1
            time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/purge_time.json',minute_value)
            ser.write(b'minuto_purga.txt=\"'+str.encode(repr(minute_value))+b'\"\xff\xff\xff')

        elif(x[2:3] == b'\x08'):
          print("plus button")
          if minute_value < 10:
            minute_value += 1
            time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/purge_time.json',minute_value)
            ser.write(b'minuto_purga.txt=\"'+str.encode(repr(minute_value))+b'\"\xff\xff\xff')

