
import paho.mqtt.client as mqtt
import json
import time
import argparse
import os

## Esta funcion devuelve la hora actual del sistema para determinar si el AC se activa o no
def getHour():
   from datetime import datetime
   return int((((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[0])


def on_message_acControlTopic_Callback(client, userdata, message):
   #print("Message Recieved: "+message.payload.decode())
   payload = json.loads(message.payload.decode())
   print("\n~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
   #acOn = 0
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
        os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ##Activa modo auto del AC
      if acOn == 0:
        print("\n~~~~ AC Turned Off! ~~~~\n")
        os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##0 apaga el aire

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

  ##Leer sht31dT 
  try:
    with open('/home/pi/aws_iot/sht31d.json','r') as f:
      sht31d_json = json.load(f)
      sht31dT = sht31d_json['t']
      print("currentTemp: "+repr(sht31dT))
      f.close()
      if currentHour >= acStartHour and currentHour <= acEndHour:
         if sht31dT >= maxT: ##Max Temp
            print("\n~~~~ AC Turned On! ~~~~\n")
            os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ##Activa modo auto del AC
         if sht31dT <= minT: ##Min Temp
            ## Cuando la temperatura <= 22 apaga el AC
            print("\n~~~~ AC Turned Off! ~~~~\n")
            os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##Apaga AC
  except Exception as e:
    print("**** acControl MQTT Client Exception: ",repr(e))
  
  time.sleep(int(refreshinterval))