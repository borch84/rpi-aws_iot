#!/usr/bin/python3
import json
import time
import serial
from threading import Timer, Thread
import RPi.GPIO as GPIO
from Atlas import atlas_i2c
import time_purge_handler_file

device = atlas_i2c(address=99,bus=1,file_path="/home/pi/aws_iot/ph99.json",sensor_type="ph")
 
class ReadSensorsThread(Timer):
  def run(self):
    while not self.finished.wait(self.interval):
      self.function(*self.args, **self.kwargs)

def read_sensors_function(ser):
    print("## reading sensors...")
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

ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5
)

read_sensors_function(ser)
sensorThread = ReadSensorsThread(10,read_sensors_function, args=(ser,)) # Read sensor data every 10s
sensorThread.start()

def purge_timer(pump_pin,ser,pump):
    GPIO.output(pump_pin,1) #Deactivate pump pin when timer finishes. 
    #ser.write(b'pump1.val=0\xff\xff\xff')
    if (pump == 'pump1'):
      ser.write(b'pump1.val=0\xff\xff\xff')
    if (pump == 'pump2'):
      ser.write(b'pump2.val=0\xff\xff\xff')


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pump1_pin = 22
pump2_pin = 23
timeout_seconds = 1
# Cada vez que el programa inicia hay que desactivar la purga para cada bomba
ser.write(b'pump1.val=0\xff\xff\xff')
ser.write(b'pump2.val=0\xff\xff\xff')
GPIO.setup(pump1_pin,GPIO.OUT)
GPIO.setup(pump2_pin,GPIO.OUT)
GPIO.output(pump1_pin,1) # 1 desactiva el relay 
GPIO.output(pump2_pin,1) 


pump1_min = 0
pump2_min = 0
pump1_min = time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/pump1_purge.json')
ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')
pump2_min = time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/pump2_purge.json')
ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')


while 1:
    x = ser.readline()
    pump1_timer = Timer(pump1_min*timeout_seconds,purge_timer,args=(pump1_pin,ser,'pump1'))    
    pump2_timer = Timer(pump2_min*timeout_seconds,purge_timer,args=(pump2_pin,ser,'pump2'))

    if (len(x) > 0):
      if (x[0:1] == b'e'):
        print("~~ event")
        print(x)
        if (x[1:2] == b'\x00'):
          print ("~~~ Main Page")
          if (x[2:3] == b'\x05'):
            print("pump 1 button")
            ser.write(b'get pump1.val\xff\xff\xff')
            x = ser.readline()
            value = x[1:2]
            if value == b'\x01':
              GPIO.output(pump1_pin,0) # 0 signal value activates relay pin            
              pump1_timer.start() # start pump1 timer

            elif value == b'\x00':
              GPIO.output(pump1_pin,1) # 1 desactiva el relay 
              ser.write(b'pump1.val=0\xff\xff\xff')
              pump1_timer.cancel()
          
          if (x[2:3] == b'\x14'):
            print("pump 2 button")
            ser.write(b'get pump2.val\xff\xff\xff')
            x = ser.readline()
            value = x[1:2]
            if value == b'\x01':
              GPIO.output(pump2_pin,0) # 0 signal value activates relay pin            
              pump2_timer.start()

            elif value == b'\x00':
              GPIO.output(pump2_pin,1) # 1 desactiva el relay 
              ser.write(b'pump2.val=0\xff\xff\xff')
              pump2_timer.cancel()

          elif(x[2:3] == b'\x01'):
            print("read ph button")
            ph = device.query('r')
            print(repr(ph))
            ser.write(b't0.txt=\"'+str.encode(repr(ph))+b'ph\"\xff\xff\xff')
          
          elif(x[2:3] == b'\x07'):
            print("minus button pump 1")
            if pump1_min > 1:
              pump1_min -= 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump1_purge.json',pump1_min)
              ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

          elif(x[2:3] == b'\x08'):
            print("plus button pump 1")
            if pump1_min < 10:
              pump1_min += 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump1_purge.json',pump1_min)
              ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

          elif(x[2:3] == b'\x12'):
            print("minus button pump 2")
            if pump2_min > 1:
              pump2_min -= 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump2_purge.json',pump2_min)
              ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')

          elif(x[2:3] == b'\x13'):
            print("plus button pump 2")
            if pump2_min < 10:
              pump2_min += 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump2_purge.json',pump2_min)
              ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')


        elif (x[1:2] == b'\x01'):
          print("~~~ PH Calibration Page")
          if (x[2:3] == b'\x05'):
            print("cal 6.86")

          if (x[2:3] == b'\x06'):
            print("cal 4.0")

          if (x[2:3] == b'\x07'):
            print("cal 9.1")

        elif (x[1:2] == b'\x02'):
          print("~~~ AC Control Page")
          if (x[2:3] == b'\x0A'):
            print("minus start time")

          if (x[2:3] == b'\x0C'):
            print("minus end time")

          if (x[2:3] == b'\x0E'):
            print("minus temp")

          if (x[2:3] == b'\x10'):
            print("minus max temp")

          if (x[2:3] == b'\x0B'):
            print("plus start time")

          if (x[2:3] == b'\x0D'):
            print("plus end time")

          if (x[2:3] == b'\x0F'):
            print("plus min temp")

          if (x[2:3] == b'\x11'):
            print("plus max temp")
