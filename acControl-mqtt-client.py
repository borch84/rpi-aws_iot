
import paho.mqtt.client as mqtt
import json
import time
import argparse
import os
import json_handler

## Esta funcion devuelve la hora actual del sistema para determinar si el AC se activa o no
def getHour():
   from datetime import datetime
   return int((((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[0])


def on_message_acControlTopic_Callback(client, userdata, message):
   print("Message Recieved: "+message.payload.decode())
   payload = json.loads(message.payload.decode())
   print("\n~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
   #acOn = 0

   if "getConfig" in payload:
     print("Get Config")
  
   global acStartHour
   global acEndHour
   global minT
   global maxT
   try:
      acStartHour = payload["acStartHour"]
      acEndHour = payload["acEndHour"]
      acOn = payload["acOn"]
      minT = payload["minT"]
      maxT = payload["maxT"]

      f = open("/home/pi/aws_iot/acControl.json","w")

      acControlJSON = ('{'+ 
                          '\"minT\":' + repr(minT) + ','
                          '\"maxT\":' + repr(maxT) + ','
                          '\"acStartHour\":' + repr(acStartHour) + ','
                          '\"acEndHour\":' + repr(acEndHour) +
                       '}')
      f.write(acControlJSON)
      f.close()      

      print("acStartHour: "+repr(acStartHour))
      print("acEndHour: "+repr(acEndHour))
      print("currentHour: "+repr(currentHour))
      print("minT: "+repr(minT))
      print("maxT: "+repr(maxT))

      if acOn == 1:
        print("\n~~~~ AC Turned On! ~~~~\n")
        # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ##Activa modo auto del AC
        os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Activa comfort zone fan
      if acOn == 0:
        print("\n~~~~ AC Turned Off! ~~~~\n")
        # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##0 apaga el aire
        os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Apaga comfort zone fan
   except KeyError as e:
      print("Exception: KeyError: ")

   print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")


## Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--broker_url", action="store", dest="broker_url", help="broker_url", required=True)
parser.add_argument("-t", "--topic", action="store", dest="topic", help="AC Control Topic", required=True)
parser.add_argument("-min", "--min_temp", action="store", dest="minT", help="Min Temperature", required=False)
parser.add_argument("-max", "--max_temp", action="store", dest="maxT", help="Max Temperature", required=False)
parser.add_argument("-acStartHour", "--acStartHour", action="store", dest="acStartHour", help="acStartHour", required=False)
parser.add_argument("-acEndHour", "--acEndHour", action="store", dest="acEndHour", help="acEndHour", required=False)
parser.add_argument("-ri", "--refreshInterval", action="store", dest="refreshinterval", required=True, help="Refresh interval in Seconds")
parser.add_argument("-acs", "--ac_status", action="store", dest="ac_status", required=False, help="AC Status On/Off")
parser.add_argument("-ena", "--enabled", action="store", dest="enabled", required=False, help="AC Enabled Status")


args = parser.parse_args()
broker_url = args.broker_url
topic = args.topic

f = open("/home/pi/aws_iot/acControl.json","r")
acControlJSON  = json.load(f)
f.close()

if args.minT != None:
  minT = int(args.minT)
else:
  minT = acControlJSON["minT"]

if args.maxT != None:
  maxT = int(args.maxT)
else:  
  maxT = acControlJSON["maxT"]

if args.acStartHour != None:
  acStartHour = int(args.acStartHour)
else:
  acStartHour = acControlJSON["acStartHour"]

if args.acEndHour != None:
  acEndHour = int(args.acEndHour)
else:  
  acEndHour = acControlJSON["acEndHour"]

if args.ac_status != None:
  ac_status = int(args.ac_status)
else:  
  ac_status = acControlJSON["ac_status"]

if args.enabled != None:
  ac_ena = bool(args.enabled)
else:  
  enabled = acControlJSON["enabled"]

refreshinterval = args.refreshinterval

broker_port = 1883
mqttClient = mqtt.Client()
mqttClient.connect(broker_url, broker_port)
mqttClient.subscribe(topic,qos=1)
mqttClient.message_callback_add(topic,on_message_acControlTopic_Callback)
mqttClient.loop_start()

while True:
  ## Implementacion del control del AC
  ## Cuando la temperatura sube >= 27.5, activa modo DRY de AC
  currentHour = getHour()
  ## Primero se revisa si el AC puede activarse con base en las horas de actividad del AC

  
  print("\n~~~~~~~~~~~ AC Control ~~~~~~~~~~~~~~")
  print("acStartHour: "+repr(acStartHour))
  print("acEndHour: "+repr(acEndHour))
  print("currentHour: "+repr(currentHour))
  print("minT: "+repr(minT))
  print("maxT: "+repr(maxT))
  print("ac_status: "+repr(ac_status))
  print("enabled: "+repr(enabled))

  ##Leer sht31dT 
  #try:
    #with open('/home/pi/aws_iot/sht31d.json','r') as f:
      #sht31d_json = json.load(f)
      #sht31dT = sht31d_json['t']

  sht31dT = json_handler.read_field("sht31d.json","t")
  print("currentTemp: "+repr(sht31dT))
  #f.close()
  if currentHour >= acStartHour and currentHour < acEndHour:
    if sht31dT >= maxT and ac_status == 0: ##Max Temp
      print("\n~~~~ AC Turned On! ~~~~\n")
      # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ## Activa AC Ciac
      os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Activa comfort zone fan
      # Save AC status in acControl.json, 1=ON
      json_handler.write_field("acControl.json",1,"ac_status")
      ac_status = 1

    if sht31dT <= minT and ac_control == 1: ##Min Temp
      ## Cuando la temperatura <= 23 apaga el AC
      print("\n~~~~ AC Turned Off! ~~~~\n")
      # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ## Apaga AC
      os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Apage comfort zone fan
      # Save AC status in acControl.json, 0=OFF
      json_handler.write_field("acControl.json",0,"ac_status")
      ac_status = 0
  
  #except Exception as e:
    #print("**** acControl MQTT Client Exception: ",repr(e))
  
  time.sleep(int(refreshinterval))
