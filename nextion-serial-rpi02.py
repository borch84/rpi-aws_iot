#!/usr/bin/python3
import json
import time
import serial
from threading import Timer, Thread, Condition, Lock, Event
import RPi.GPIO as GPIO
from Atlas import atlas_i2c
import paho.mqtt.client as mqtt
import json_handler
import subprocess

device = atlas_i2c(address=99,bus=1,file_path="/home/pi/aws_iot/ph99.json",sensor_type="ph")

class mqttThreadClass(Thread):
  def __init__(self, broker, topic, name, ac_file):
    Thread.__init__(self)
    self.name = name
    print("Init: "+self.name) 
    self.broker = broker
    self.topic = topic
    self.ac_file = ac_file
    #flag to pause thread
    self.paused = False
    # Explicitly using Lock over RLock since the use of self.paused
    # break reentrancy anyway, and I believe using Lock could allow
    # one thread to pause the worker, while another resumes; haven't
    # checked if Condition imposes additional limitations that would 
    # prevent that. In Python 2, use of Lock instead of RLock also
    # boosts performance.
    self.pause_cond = Condition(Lock())

    # Initializes MQTT Broker Connection
    broker_port = 1883
    self.mqttClient = mqtt.Client()
    self.mqttClient.connect(broker, broker_port)
    self.mqttClient.subscribe(topic,qos=1)
    self.mqttClient.message_callback_add(topic,self.on_message_acControlTopic_Callback)
    self.mqttClient.loop_start()
    print(self.name+": Connected to MQTT Broker "+broker)

  def run(self):
      print("Start: "+self.name) 
      while True:
          with self.pause_cond:
              while self.paused:
                self.pause_cond.wait()

              #TODO: MQTT Job
              #not paused
              #print (self.name)
          #time.sleep(5)
  
  def on_message_acControlTopic_Callback(self, client, userdata, message):
    print("\n~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
    print("Message Recieved: "+message.payload.decode())
    payload = json.loads(message.payload.decode())
    #TODO
    if "getConfig" in payload:
     print("Send Config to MQTT Topic: getConfigTopic")
     self.mqttClient.publish("getConfigTopic",payload='{"JSON":true}',qos=0, retain=False)

class ReadSensorsThread(Timer):
  def __init__(self, interval, function, args, name):
    Timer.__init__(self, interval, function)
    self.name = name
    print("Init: "+self.name)
    self.interval = interval
    self.function = function
    self.args = args
    self.can_run = Event()
    self.can_run.set()

  def run(self):
    print("Start: "+self.name)
    self.can_run.wait()
    while not self.finished.wait(self.interval):
      self.function(*self.args, **self.kwargs)

  def pause(self):
    print("Pause: "+self.name)
    self.can_run.clear()

  def resume(self):
    print("Resume: "+self.name)
    self.can_run.set()

def getJSONValues(file,list_fields):
  fields_values = []
  try:
    with open(file,'r') as f:
      json_data = json.load(f)
      f.close()
    for field in list_fields:
      fields_values.append(json_data[field])
    return fields_values
  except Exception as e:
    print("getJSONValues Exception: "+repr(e))
    return None


def read_sensors_function(ser):
    print("## reading sensors...")
    # Read CPU Core Temp
    core_temp = getJSONValues('/home/pi/aws_iot/rpi-cpu-core-temp.log',['CPUTemp'])
    if core_temp is not None:
      ser.write(b't2.txt=\"' + str.encode(repr(core_temp[0])) + b'C\"\xff\xff\xff')

    # Read File System utilization
    fs_util = getJSONValues('/home/pi/aws_iot/fs_usage.json',['fs_usage'])
    if fs_util is not None:
      ser.write(b'fs_utilization.txt=\"' + str.encode(repr(fs_util[0])) + b'%\"\xff\xff\xff')

    # Read SHT31D Sensor Data File
    t, h = getJSONValues('/home/pi/aws_iot/sht31d.json',['t','h'])
    if t is not None and h is not None:
      ser.write(b't5.txt=\"' + str.encode(repr(t)) + b'C\"\xff\xff\xff')
      ser.write(b't7.txt=\"' + str.encode(repr(h)) + b'%\"\xff\xff\xff')
    
    # Read PH Sensor Data File
    ph99 = getJSONValues('/home/pi/aws_iot/ph99.json',['ph'])
    if ph99 is not None:
      ser.write(b'ph_result.txt=\"'+str.encode(repr(ph99[0]))+b'\"\xff\xff\xff')


ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5
)

read_sensors_function(ser)
sensorThread = ReadSensorsThread(interval=10,function=read_sensors_function, args=(ser,),name="SENSOR-THREAD") # Read sensor data every 10s
sensorThread.start()

mqttThreadObject = mqttThreadClass(broker="192.168.4.203", topic="acControlTopic", name="MQTT-AC-THREAD", ac_file="/home/pi/aws_iot/acControl.json")
mqttThreadObject.start()

# Test Pause sensor thread
# sensorThread.pause()
# time.sleep(15)
# sensorThread.resume()

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
timeout_seconds = 60
# Cada vez que el programa inicia hay que desactivar la purga para cada bomba
ser.write(b'pump1.val=0\xff\xff\xff')
ser.write(b'pump2.val=0\xff\xff\xff')
GPIO.setup(pump1_pin,GPIO.OUT)
GPIO.setup(pump2_pin,GPIO.OUT)
GPIO.output(pump1_pin,1) # 1 desactiva el relay 
GPIO.output(pump2_pin,1) 


# Relay Control Variables
pump1_start_hour, pump1_min, pump1_enabled = getJSONValues('pump1_purge.json',['start_hour','min','enabled'])
pump2_start_hour, pump2_min, pump2_enabled = getJSONValues('pump2_purge.json',['start_hour','min','enabled'])

# Set Nextion AC Ctrl Page's labels 
def setNextionACVars(ser,ac_st,ac_et,ac_min,ac_ena,ac_status):
  ser.write(b'ac_st.txt=\"'+str.encode(repr(ac_st))+b'\"\xff\xff\xff')
  ser.write(b'ac_et.txt=\"'+str.encode(repr(ac_et))+b'\"\xff\xff\xff')
  ser.write(b'ac_min.txt=\"'+str.encode(repr(ac_min))+b'\"\xff\xff\xff')
  ser.write(b'ac_max.txt=\"'+str.encode(repr(ac_max))+b'\"\xff\xff\xff')
  if ac_ena:
    ser.write(b'ac_enabled.val=1\xff\xff\xff')
    ser.write(b'ac_enabled.txt="Disable AC"\xff\xff\xff')
  if not ac_ena:
    ser.write(b'ac_enabled.val=0\xff\xff\xff')
    ser.write(b'ac_enabled.txt="Enable AC"\xff\xff\xff')
  if ac_status == 0:
    ser.write(b'ac_ctrl.txt="Start AC"\xff\xff\xff')
    ser.write(b'ac_ctrl.val=0\xff\xff\xff')
  if ac_status == 1:
    ser.write(b'ac_ctrl.txt="Stop AC"\xff\xff\xff')
    ser.write(b'ac_ctrl.val=1\xff\xff\xff')

# AC Control Variables
# ac_st = 6
# ac_et = 18
# ac_min = 23
# ac_max = 27
# ac_ena = True
# ac_status = 0

ac_st, ac_et, ac_min, ac_max, ac_ena, ac_status = getJSONValues('/home/pi/aws_iot/acControl.json',['acStartHour','acEndHour','minT','maxT','enabled','ac_status'])
setNextionACVars(ser,ac_st,ac_et,ac_min,ac_ena,ac_status)


while 1:
    x = ser.readline()

    pump1_timer = Timer(pump1_min*timeout_seconds,purge_timer,args=(pump1_pin,ser,'pump1'))    
    pump2_timer = Timer(pump2_min*timeout_seconds,purge_timer,args=(pump2_pin,ser,'pump2'))

    if (len(x) > 0):
      if (x[0:1] == b'e'):

        # Pause the Sensor Thread after we got data from Nextion Serial, so it won't make noise during Nextion operations
        sensorThread.pause()

        print("~~ event")
        print(x)
####### Main Page ###############
        if (x[1:2] == b'\x00'):
          print ("~~~ Main Page")
          if (x[2:3] == b'\x01'):
            print("ph button")
            ser.write(b'ph_result.txt=\"'+str.encode(repr(getJSONValues('/home/pi/aws_iot/ph99.json',['ph'])[0]))+b'\"\xff\xff\xff')
          
          if (x[2:3] == b'\x02'):
            print("ac control button")
            setNextionACVars(ser,ac_st,ac_et,ac_min,ac_ena,ac_status)

          if (x[2:3] == b'\x07'):
            print("r_ctrl button")
            ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')
            ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')
            ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')
            ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')
            if pump1_enabled:
              ser.write(b'p1_cb.val=1\xff\xff\xff')
            else:
              ser.write(b'p1_cb.val=0\xff\xff\xff')
            if pump2_enabled:
              ser.write(b'p2_cb.val=1\xff\xff\xff')
            else:
              ser.write(b'p2_cb.val=0\xff\xff\xff')


          if (x[2:3] == b'\x06'):
            print("sht31d button")
            t, h = getJSONValues('/home/pi/aws_iot/sht31d.json',['t','h'])
            ser.write(b't5.txt=\"' + str.encode(repr(t)) + b'C\"\xff\xff\xff')
            ser.write(b't7.txt=\"' + str.encode(repr(h)) + b'%\"\xff\xff\xff')

          
          if (x[2:3] == b'\x09'):
            print("rpi status button")
            core_temp = json_handler.read_field('/home/pi/aws_iot/rpi-cpu-core-temp.log','CPUTemp')
            ser.write(b't2.txt=\"' + str.encode(repr(core_temp)) + b'C\"\xff\xff\xff')
            fs_util = json_handler.read_field('/home/pi/aws_iot/fs_usage.json','fs_usage')
            ser.write(b'fs_utilization.txt=\"' + str.encode(repr(fs_util)) + b'%\"\xff\xff\xff')

######## R Ctrl Page ###############
        if (x[1:2] == b'\x01'):
          print ("~~~ R_Ctrl Page")

          if (x[2:3] == b'\x13'):
            print("pump1 checkbox")
            if pump1_enabled == 1:
              pump1_enabled = 0
            else:
              pump1_enabled = 1
            json_handler.write_field('pump1_purge.json',pump1_enabled,'enabled')

          if (x[2:3] == b'\x14'):
            print("pump2 checkbox")
            if pump2_enabled == 1:
              pump2_enabled = 0
            else:
              pump2_enabled = 1
            json_handler.write_field('pump2_purge.json',pump2_enabled,'enabled')

          if (x[2:3] == b'\x01'):
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
          
          if (x[2:3] == b'\x09'):
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

          
          if(x[2:3] == b'\x03'):
            print("minus button pump 1")
            if pump1_min > 1:
              pump1_min -= 1
              json_handler.write_field('/home/pi/aws_iot/pump1_purge.json',pump1_min,'min')
              ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x04'):
            print("plus button pump 1")
            if pump1_min < 10:
              pump1_min += 1
              json_handler.write_field('/home/pi/aws_iot/pump1_purge.json',pump1_min,'min')
              ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x07'):
            print("minus button pump 2")
            if pump2_min > 1:
              pump2_min -= 1
              json_handler.write_field('/home/pi/aws_iot/pump2_purge.json',pump2_min,'min')
              ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x08'):
            print("plus button pump 2")
            if pump2_min < 10:
              pump2_min += 1
              json_handler.write_field('/home/pi/aws_iot/pump2_purge.json',pump2_min,'min')
              ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')
          
          if(x[2:3] == b'\x0D'):
            print("minus start hour pump1")
            if pump1_start_hour > 0:
              pump1_start_hour -= 1
              json_handler.write_field('/home/pi/aws_iot/pump1_purge.json',pump1_start_hour,'start_hour')
              ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x0E'):
            print("plus start hour pump1")
            if pump1_start_hour < 23:
              pump1_start_hour += 1
              json_handler.write_field('/home/pi/aws_iot/pump1_purge.json',pump1_start_hour,'start_hour')
              ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x0F'):
            print("minus start hour pump2")
            if pump2_start_hour > 0:
              pump2_start_hour -= 1
              json_handler.write_field('/home/pi/aws_iot/pump2_purge.json',pump2_start_hour,'start_hour')
              ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x10'):
            print("plus start hour pump2")
            if pump2_start_hour < 23:
              pump2_start_hour += 1
              json_handler.write_field('/home/pi/aws_iot/pump2_purge.json',pump2_start_hour,'start_hour')
              ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x15'):
            print("save cfg")
            with open("pi_crontab_bigplant", 'w') as f:
              if pump1_enabled:
                f.write("0 "+ str(pump1_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 22 -j pump1_purge.json\n") 
              else:
                f.write("# 0 "+ str(pump1_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 22 -j pump1_purge.json\n") 
              f.close()
              subprocess.run(["sudo", "cp", "pi_crontab_bigplant", "/etc/cron.d/"]) 
            with open("pi_crontab_smallplant", 'w') as f:
              if pump2_enabled:
                f.write("0 "+ str(pump2_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 23 -j pump2_purge.json\n") 
              else:
                f.write("# 0 "+ str(pump2_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 23 -j pump2_purge.json\n") 
              f.close()
              subprocess.run(["sudo", "cp", "pi_crontab_smallplant", "/etc/cron.d/"]) 

######## PH Page ###############
        if (x[1:2] == b'\x02'):
          print("~~~ PH Calibration Page")
          if (x[2:3] == b'\x03'):
            print("cal 6.86")

          if (x[2:3] == b'\x04'):
            print("cal 4.0")

          if (x[2:3] == b'\x05'):
            print("cal 9.1")
          
          if(x[2:3] == b'\x07'):
            print("read ph button")
            ph = device.query('r')
            print(repr(ph))
            ser.write(b'ph_result.txt=\"'+str.encode(repr(ph))+b'\"\xff\xff\xff')

######## AC Ctrl Page ###############
        if (x[1:2] == b'\x03'):
          print("~~~ AC Control Page")
          if (x[2:3] == b'\x07'):
            print("minus start time")
            if ac_st > 0:
              ac_st -= 1
              ser.write(b'ac_st.txt=\"'+str.encode(repr(ac_st))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x09'):
            print("minus end time")
            if ac_et > 0:
              ac_et -= 1
              ser.write(b'ac_et.txt=\"'+str.encode(repr(ac_et))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x0B'):
            print("minimum temp - minus button")
            if ac_min > 20:
              ac_min -= 1
              ser.write(b'ac_min.txt=\"'+str.encode(repr(ac_min))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x0D'):
            print("max temp - minus button")
            if ac_max > 20:
              ac_max -= 1
              ser.write(b'ac_max.txt=\"'+str.encode(repr(ac_max))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x08'):
            print("plus start time")
            if ac_st < 23:
              ac_st +=1
              ser.write(b'ac_st.txt=\"'+str.encode(repr(ac_st))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x0A'):
            print("plus end time")
            if ac_et < 23:
              ac_et += 1
              ser.write(b'ac_et.txt=\"'+str.encode(repr(ac_et))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x0C'):
            print("plus min temp")
            if ac_min < 29:
              ac_min += 1
              ser.write(b'ac_min.txt=\"'+str.encode(repr(ac_min))+b'\"\xff\xff\xff')

          if (x[2:3] == b'\x0E'):
            print("plus max temp")
            if ac_max < 29:
              ac_max += 1
              ser.write(b'ac_max.txt=\"'+str.encode(repr(ac_max))+b'\"\xff\xff\xff')
          
          if (x[2:3] == b'\x10'):
            print("save ac control button")
            try:
              with open("acControl.json",'r') as f:
                json_data = json.load(f)
                f.close()
              json_data['minT'] = ac_min
              json_data['maxT'] = ac_max
              json_data['acStartHour'] = ac_st
              json_data['acEndHour'] = ac_et
              json_data['enabled'] = ac_ena

              with open("acControl.json",'w') as f:
                json.dump(json_data,f)
                f.close()
              
              if ac_ena:
                with open("acControl-watchdog-crontab",'w') as f:
                  f.write("* * * * * pi /home/pi/aws_iot/acControl-watchdog.sh\n")
                  f.close()

              if not ac_ena:
                with open("acControl-watchdog-crontab",'w') as f:
                  f.write("#* * * * * pi /home/pi/aws_iot/acControl-watchdog.sh\n")
                  f.close()
                  subprocess.run(["sh", "acControl-disable.sh"])

              subprocess.run(["sudo", "cp", "acControl-watchdog-crontab", "/etc/cron.d/"]) 

            except Exception as e:
                print("**** Exception writing json file: "+repr(e))
                

          if (x[2:3] == b'\x11'):
            print("enable/disable ac control")
            ac_ena = not ac_ena
            if ac_ena:
              ser.write(b'ac_enabled.txt="Disable AC"\xff\xff\xff')
            if not ac_ena:
              ser.write(b'ac_enabled.txt="Enable AC"\xff\xff\xff')

          if (x[2:3] == b'\x0F'):
            ser.write(b'get ac_ctrl.val\xff\xff\xff')
            x = ser.readline()
            value = x[1:2]
            if value == b'\x01':
              print("start ac")
              json_handler.write_field("acControl.json",1,"ac_status")
              ac_status = 1
              #subprocess.run(["python3", "rpi-i2c-cron.py", "1"]) # Ciac AC Start Signal
              subprocess.run(["python3", "rpi-i2c-cron.py", "i"]) # Comfort Zone Tower Fan
              ser.write(b'ac_ctrl.txt="Stop AC"\xff\xff\xff')
 
            if value == b'\x00':
              print("stop ac")
              json_handler.write_field("acControl.json",0,"ac_status")
              ac_status = 0
              ser.write(b'ac_ctrl.txt="Start AC"\xff\xff\xff')
              #subprocess.run(["python3", "rpi-i2c-cron.py", "0"]) # Ciac AC Stop Signal
              subprocess.run(["python3", "rpi-i2c-cron.py", "i"]) # Comfort Zone Tower Fan
    
######## Resume the Sensor Reading Thread:
        sensorThread.resume()