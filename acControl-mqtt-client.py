
import paho.mqtt.client as mqtt
import json
import time
import argparse
import os
import json_handler
from utils import getJSONValues, save_acControl

## Esta funcion devuelve la hora actual del sistema para determinar si el AC se activa o no
def getHour():
   from datetime import datetime
   return int((((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[0])

  
def on_message_acStatusTopic_Callback(client, userdata, message):
  payload = json.loads(message.payload.decode())
  print("\n~~~~ on_message_mqtt_acStatusTopic_Callback ~~~~")

  ac_status = json_handler.read_field('/home/pi/aws_iot/acControl.json','ac_status')
  if ac_status == 0:
    # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ##Activa modo auto del AC
    os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Activa comfort zone fan
    print("\n~~~~ AC Turned On! ~~~~\n")
    ac_status = 1
  elif ac_status == 1:
    # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##0 apaga el aire
    os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Apaga comfort zone fan
    print("\n~~~~ AC Turned Off! ~~~~\n")
    ac_status = 0
  json_handler.write_field('/home/pi/aws_iot/acControl.json',ac_status,'ac_status')
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

def on_message_acControlTopic_Callback(client, userdata, message):
  print("\n~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
  print("Message Recieved: "+message.payload.decode())
  payload = json.loads(message.payload.decode())
  
  if "getConfig" in payload:
    print("Get Config")
    print("Send Config to MQTT Topic: getConfigTopic")
    with open('/home/pi/aws_iot/acControl.json','r') as f:
      json_payload = f.read()
      f.close()
    client.publish("getConfigTopic",payload=json_payload,qos=0, retain=False)
  
  if "newConfig" in payload:
    save_acControl('/home/pi/aws_iot/acControl.json',payload['newConfig'])
   
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")


## Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--broker", action="store", dest="broker", help="broker url", required=False)
parser.add_argument("-bp", "--broker_port", action="store", dest="broker_port", help="broker port", required=False)
parser.add_argument("-t", "--topic", action="store", dest="topic", help="AC Control Topic", required=False)
parser.add_argument("-min", "--min_temp", action="store", dest="minT", help="Min Temperature", required=False)
parser.add_argument("-max", "--max_temp", action="store", dest="maxT", help="Max Temperature", required=False)
parser.add_argument("-acStartHour", "--acStartHour", action="store", dest="acStartHour", help="acStartHour", required=False)
parser.add_argument("-acEndHour", "--acEndHour", action="store", dest="acEndHour", help="acEndHour", required=False)
parser.add_argument("-ri", "--refreshInterval", action="store", dest="refresh_interval", required=False, help="Refresh interval in Seconds")
parser.add_argument("-acs", "--ac_status", action="store", dest="ac_status", required=False, help="AC Status On/Off")
parser.add_argument("-ena", "--enabled", action="store", dest="enabled", required=False, help="AC Enabled Status")


args = parser.parse_args()

acStartHour, acEndHour, minT, maxT, enabled, ac_status, broker, broker_port, topic, refresh_interval = getJSONValues('/home/pi/aws_iot/acControl.json',['acStartHour','acEndHour','minT','maxT','enabled','ac_status', 'broker', 'broker_port', 'topic', 'refresh_interval'])


if args.minT != None:
  minT = int(args.minT)

if args.maxT != None:
  maxT = int(args.maxT)

if args.acStartHour != None:
  acStartHour = int(args.acStartHour)

if args.acEndHour != None:
  acEndHour = int(args.acEndHour)

if args.ac_status != None:
  ac_status = int(args.ac_status)

if args.enabled != None:
  enabled = bool(args.enabled)

if args.broker != None:
  broker = args.broker

if args.broker_port != None:
  broker_port = args.broker_port

if args.topic != None:
  topic = args.topic

if args.refresh_interval != None:
  refresh_interval = int(args.refresh_interval)

mqttClient = mqtt.Client()
mqttClient.connect(broker, broker_port)
mqttClient.subscribe(topic,qos=1)
mqttClient.message_callback_add(topic,on_message_acControlTopic_Callback)
mqttClient.subscribe("acStatusTopic",qos=1)
mqttClient.message_callback_add("acStatusTopic",on_message_acStatusTopic_Callback)
mqttClient.loop_start()


counter = 0

while True:
  ## Implementacion del control del AC
  ## Cuando la temperatura sube >= 27.5, activa modo DRY de AC
  currentHour = getHour()
  ## Primero se revisa si el AC puede activarse con base en las horas de actividad del AC

  
  print("\n~~~~~~~~~~~ AC Control ~~~~~~~~~~~~~~")
  acStartHour, acEndHour, minT, maxT, enabled, ac_status, refresh_interval = getJSONValues('/home/pi/aws_iot/acControl.json',['acStartHour','acEndHour','minT','maxT','enabled','ac_status', 'refresh_interval'])

  print("acStartHour: "+repr(acStartHour))
  print("acEndHour: "+repr(acEndHour))
  print("currentHour: "+repr(currentHour))
  print("minT: "+repr(minT))
  print("maxT: "+repr(maxT))
  print("ac_status: "+repr(ac_status))
  print("enabled: "+repr(enabled))
  print("broker " + broker)
  print("topic: "+ topic)

  sht31dT = json_handler.read_field("sht31d.json","t")
  print("currentTemp: "+repr(sht31dT))
  if enabled: # this means we want Rpi to control the AC. 
    if currentHour >= acStartHour and currentHour < acEndHour:
      if sht31dT >= maxT and ac_status == 0: ##Max Temp
        print("\n~~~~ AC Turned On! ~~~~\n")
        # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ## Activa AC Ciac
        os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Activa comfort zone fan
        # Send ac_status to nodered to update the UI:
        j ="{\"ac_status\": "+str(1)+", \"sht31dT\":" + str(sht31dT) + "}"
        mqttClient.publish("getConfigTopic",payload=j,qos=0, retain=False)
        json_handler.write_field('/home/pi/aws_iot/acControl.json',1,'ac_status')

      if sht31dT <= minT and ac_status == 1: ##Min Temp
        ## Cuando la temperatura <= 23 apaga el AC
        print("\n~~~~ AC Turned Off! ~~~~\n")
        # os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ## Apaga AC
        os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py i") ## Apage comfort zone fan
        # Send ac_status to nodered to update the UI:
        j ="{\"ac_status\": "+str(0)+", \"sht31dT\":" + str(sht31dT) + "}"
        mqttClient.publish("getConfigTopic",payload=j,qos=0, retain=False)
        json_handler.write_field('/home/pi/aws_iot/acControl.json',0,'ac_status')
 

  time.sleep(refresh_interval)
