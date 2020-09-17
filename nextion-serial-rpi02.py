#!/usr/bin/python3
import json
import time
import serial
from threading import Timer, Thread
import RPi.GPIO as GPIO
from Atlas import atlas_i2c
import time_purge_handler_file
import subprocess

device = atlas_i2c(address=99,bus=1,file_path="/home/pi/aws_iot/ph99.json",sensor_type="ph")
 
class ReadSensorsThread(Timer):
  def run(self):
    while not self.finished.wait(self.interval):
      self.function(*self.args, **self.kwargs)

def update_crontab(line, crontab):
  print("update_crontab")
  #subprocess.run(["/bin/sh", update_script]) # ansible test
  with open(crontab, 'w') as f:
    f.write(line)
    f.close()
  subprocess.run(["sudo", "cp", crontab, "/etc/cron.d/"]) 

def read_sensors_function(ser):
    print("## reading sensors...")
    try: 
      with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
        core_temp_json = json.load(f)
        f.close()
        ser.write(b't2.txt=\"' + str.encode(repr(core_temp_json['CPUTemp'])) + b'C\"\xff\xff\xff')
    except Exception as e:
      print("!!! read rpi cpu core log file exception: ",repr(e))

    try:
      with open('/home/pi/aws_iot/fs_usage.json','r') as f:
        fs_json = json.load(f)
        f.close()
        ser.write(b'fs_utilization.txt=\"' + str.encode(repr(fs_json['fs_usage'])) + b'%\"\xff\xff\xff')
    except Exception as e:
      print("Read fs_usage.json file exception: ",repr(e))

    try: 
      with open('/home/pi/aws_iot/sht31d.json','r') as f:
        sht31d_json = json.load(f)
        f.close()
        ser.write(b't5.txt=\"' + str.encode(repr(sht31d_json['t'])) + b'C\"\xff\xff\xff')
        ser.write(b't7.txt=\"' + str.encode(repr(sht31d_json['h'])) + b'%\"\xff\xff\xff')
    except Exception as e:
      print("!!! read sht31d.log file exception: ",repr(e))
    
    
    try:
      with open('/home/pi/aws_iot/ph99.json','r') as f:
        ph99_json = json.load(f)
        f.close()
        ser.write(b'ph_result.txt=\"'+str.encode(repr(ph99_json['ph']))+b'\"\xff\xff\xff')
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
timeout_seconds = 60
# Cada vez que el programa inicia hay que desactivar la purga para cada bomba
ser.write(b'pump1.val=0\xff\xff\xff')
ser.write(b'pump2.val=0\xff\xff\xff')
GPIO.setup(pump1_pin,GPIO.OUT)
GPIO.setup(pump2_pin,GPIO.OUT)
GPIO.output(pump1_pin,1) # 1 desactiva el relay 
GPIO.output(pump2_pin,1) 


# Relay Control Variables
try: 
  with open('pump1_purge.json','r') as f:
    pump1_json = json.load(f)
    f.close()
    pump1_start_hour = pump1_json['start_hour']
    pump1_min = pump1_json['min']
    pump1_enabled = pump1_json['enabled']
    ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')
    ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')
    ser.write(b'p1_cb.val='+str.encode(repr(pump1_enabled))+b'\xff\xff\xff')
    if pump1_enabled:
      ser.write(b'p1_cb.val=1\xff\xff\xff')
    else:
      ser.write(b'p1_cb.val=0\xff\xff\xff')
except Exception as e:
  print("!!! read pump1_purge.json log file exception: ",repr(e)) 

try: 
  with open('pump2_purge.json','r') as f:
    pump1_json = json.load(f)
    f.close()
    pump2_start_hour = pump1_json['start_hour']
    pump2_min = pump1_json['min']
    pump2_enabled = pump1_json['enabled']
    ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')
    ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')
    if pump2_enabled:
      ser.write(b'p2_cb.val=1\xff\xff\xff')
    else:
      ser.write(b'p2_cb.val=0\xff\xff\xff')
except Exception as e:
  print("!!! read pump2_purge.json file exception: ",repr(e)) 

#pump1_start_hour = 0
#pump1_start_hour = int(time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/pump1_purge.json','start_hour'))
#ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')

#pump2_start_hour = 0
#pump2_start_hour = int(time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/pump2_purge.json','start_hour'))
#ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')

#pump1_min = 0
#pump1_min = int(time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/pump1_purge.json','min'))
#ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

#pump2_min = 0
#pump2_min = int(time_purge_handler_file.read_purge_time_json('/home/pi/aws_iot/pump2_purge.json','min'))
#ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')




# AC Control Variables
ac_st = 6
ac_et = 18
ac_min = 23
ac_max = 27
ac_ena = True

try:
  with open('/home/pi/aws_iot/acControl.json','r') as f:
    accontrol_json = json.load(f)
    f.close()
    ac_st = accontrol_json['acStartHour']
    ac_et = accontrol_json['acEndHour']
    ac_min = accontrol_json['minT']
    ac_max = accontrol_json['maxT']
    ac_ena = accontrol_json['enabled']
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
except Exception as e:
  print("!!! read acControl.json file exception: ",repr(e))

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
          if (x[2:3] == b'\x01'):
            print("ph button")
            try:
              with open('/home/pi/aws_iot/ph99.json','r') as f:
                ph99_json = json.load(f)
                f.close()
                ser.write(b'ph_result.txt=\"'+str.encode(repr(ph99_json['ph']))+b'\"\xff\xff\xff')
            except Exception as e:
              print("!!! read ph99.json file exception: ",repr(e))
          
          if (x[2:3] == b'\x02'):
            print("ac control button")
            try:
              with open('/home/pi/aws_iot/acControl.json','r') as f:
                accontrol_json = json.load(f)
                f.close()
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
            except Exception as e:
              print("!!! read acControl.json file exception: ",repr(e))

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
            try: 
              with open('/home/pi/aws_iot/sht31d.json','r') as f:
                sht31d_json = json.load(f)
                f.close()
                ser.write(b't5.txt=\"' + str.encode(repr(sht31d_json['t'])) + b'C\"\xff\xff\xff')
                ser.write(b't7.txt=\"' + str.encode(repr(sht31d_json['h'])) + b'%\"\xff\xff\xff')
            except Exception as e:
              print("!!! read sht31d.log file exception: ",repr(e))
          
          if (x[2:3] == b'\x09'):
            print("rpi status button")
            try: 
              with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
                core_temp_json = json.load(f)
                f.close()
                ser.write(b't2.txt=\"' + str.encode(repr(core_temp_json['CPUTemp'])) + b'C\"\xff\xff\xff')
            except Exception as e:
              print("!!! read rpi cpu core log file exception: ",repr(e))

            try:
              with open('/home/pi/aws_iot/fs_usage.json','r') as f:
                fs_json = json.load(f)
                f.close()
                ser.write(b'fs_utilization.txt=\"' + str.encode(repr(fs_json['fs_usage'])) + b'%\"\xff\xff\xff')
            except Exception as e:
              print("Read fs_usage.json file exception: ",repr(e))

        if (x[1:2] == b'\x01'):
          print ("~~~ R_Ctrl Page")

          if (x[2:3] == b'\x13'):
            print("pump1 checkbox")
            if pump1_enabled == 1:
              pump1_enabled = 0
            else:
              pump1_enabled = 1
            time_purge_handler_file.write_purge_time_json('pump1_purge.json',pump1_enabled,'enabled')

          if (x[2:3] == b'\x14'):
            print("pump2 checkbox")
            if pump2_enabled == 1:
              pump2_enabled = 0
            else:
              pump2_enabled = 1
            time_purge_handler_file.write_purge_time_json('pump2_purge.json',pump2_enabled,'enabled')

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
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump1_purge.json',pump1_min,'min')
              ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x04'):
            print("plus button pump 1")
            if pump1_min < 10:
              pump1_min += 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump1_purge.json',pump1_min,'min')
              ser.write(b'pump1_min.txt=\"'+str.encode(repr(pump1_min))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x07'):
            print("minus button pump 2")
            if pump2_min > 1:
              pump2_min -= 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump2_purge.json',pump2_min,'min')
              ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')

          if(x[2:3] == b'\x08'):
            print("plus button pump 2")
            if pump2_min < 10:
              pump2_min += 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump2_purge.json',pump2_min,'min')
              ser.write(b'pump2_min.txt=\"'+str.encode(repr(pump2_min))+b'\"\xff\xff\xff')
          
          if(x[2:3] == b'\x0D'):
            print("minus runtime pump1")
            if pump1_start_hour > 0:
              pump1_start_hour -= 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump1_purge.json',pump1_start_hour,'start_hour')
              ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')
              #update_crontab("0 "+ str(pump1_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 22 -j pump1_purge.json\n", "pi_crontab_bigplant")


          if(x[2:3] == b'\x0E'):
            print("plus runtime pump1")
            if pump1_start_hour < 23:
              pump1_start_hour += 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump1_purge.json',pump1_start_hour,'start_hour')
              ser.write(b'p1_time.txt=\"'+str.encode(repr(pump1_start_hour))+b'\"\xff\xff\xff')
              #update_crontab("0 "+ str(pump1_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 22 -j pump1_purge.json\n", "pi_crontab_bigplant")

          if(x[2:3] == b'\x0F'):
            print("minus runtime pump2")
            if pump2_start_hour > 0:
              pump2_start_hour -= 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump2_purge.json',pump2_start_hour,'start_hour')
              ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')
              #update_crontab("0 "+ str(pump2_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 23 -j pump2_purge.json\n", "pi_crontab_smallplant")

          if(x[2:3] == b'\x10'):
            print("plus runtime pump2")
            if pump2_start_hour < 23:
              pump2_start_hour += 1
              time_purge_handler_file.write_purge_time_json('/home/pi/aws_iot/pump2_purge.json',pump2_start_hour,'start_hour')
              ser.write(b'p2_time.txt=\"'+str.encode(repr(pump2_start_hour))+b'\"\xff\xff\xff')
              #update_crontab("0 "+ str(pump2_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 23 -j pump2_purge.json\n", "pi_crontab_smallplant")

          if(x[2:3] == b'\x15'):
            print("save cfg")
            #update_crontab("0 "+ str(pump1_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 22 -j pump1_purge.json\n", "pi_crontab_bigplant")
            #update_crontab("0 "+ str(pump2_start_hour) + " * * * pi /usr/bin/python3 /home/pi/aws_iot/activate-waterpump-relay.py -p 23 -j pump2_purge.json\n", "pi_crontab_smallplant")
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

        elif (x[1:2] == b'\x02'):
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

        elif (x[1:2] == b'\x03'):
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
                  subprocess.run(["sh", "acControl-stop.sh"])

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
              #subprocess.run(["python3", "rpi-i2c-cron.py", "1"]) # Ciac AC Start Signal
              subprocess.run(["python3", "rpi-i2c-cron.py", "i"]) # Comfort Zone Tower Fan
              ser.write(b'ac_ctrl.txt="Stop AC"\xff\xff\xff')

            elif value == b'\x00':
              print("stop ac")
              ser.write(b'ac_ctrl.txt="Start AC"\xff\xff\xff')
              #subprocess.run(["python3", "rpi-i2c-cron.py", "0"]) # Ciac AC Stop Signal
              subprocess.run(["python3", "rpi-i2c-cron.py", "i"]) # Comfort Zone Tower Fan
