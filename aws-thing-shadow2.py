#!/usr/bin/env python3
'''
Jorge Alvarado
11/28/2019

## Este programa lee la informacion de los sensores:

sht31d
sps30
ds18b20
dht22
levelswitch: recibe un update del topic mqtt esp32/levelswitch. El esp32 comunica al mqtt broker aws-rpi02
el valor detectado por el sensor de nivel de agua.

reedswitch

## La informacion se actualiza en el shadow document del dispositivo IoT definido en AWS

## Este programa tambien controla el AC con base en la temperatura reportada por el sensor SHT31D

https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/html/index.html#module-AWSIoTPythonSDK.core.shadow.deviceShadow

'''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
import argparse

import os
import glob
#import sys
import paho.mqtt.client as mqtt 


## Se comento codigo referente a DHT22 porque falla mucho
## https://github.com/adafruit/Adafruit_CircuitPython_DHT
#import adafruit_dht
#dht22 = adafruit_dht.DHT22(19)


##RPi.GPIO
##Para la activacion de los relays, se va a implementar la libreria RPi.GPIO porque permite el acceso concurrent $
import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#RPi.GPIO la bomba esta conectado al pin 15 = GPIO22
waterpumpPin = 22
GPIO.setup(waterpumpPin, GPIO.OUT)
GPIO.output(waterpumpPin,1) #1=apaga la bomba


##Sensirion SHT31D
import board
import busio #https://circuitpython.readthedocs.io/en/latest/shared-bindings/busio/__init__.html#module-busio
import adafruit_sht31d
i2c = busio.I2C(board.SCL, board.SDA)
#https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity-sensor-breakout/python-circuitpython
sht31d = adafruit_sht31d.SHT31D(i2c)


##reedswitch
from gpiozero import DigitalInputDevice
reedswitch_state = False
old_reedswitch_state = False
def reedswitch_closed():
    print("reed switch i.s closed!")
    global reedswitch_state
    reedswitch_state = True
def reedswitch_opened():
    print("reed switch is opened!")
    global reedswitch_state
    reedswitch_state = False
reedswitch = DigitalInputDevice(17,pull_up=True, bounce_time=1)
reedswitch.when_activated = reedswitch_closed
reedswitch.when_deactivated = reedswitch_opened


##ds18b20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
ds18b20_folder = glob.glob(base_dir + '28*')[0]
ds18b20_file = ds18b20_folder + '/w1_slave'
def read_temp_ds18b20_raw():
    f = open(ds18b20_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_ds18b20():
    lines = read_temp_ds18b20_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_ds18b20_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f


##AWS IoT Callbacks
def customShadowCallback_Update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    print("~~~~ customShadowCallback_Update ~~~~")
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("Update request with token: " + token + " accepted!")
        #print("reported reedswitch state: " + str(payloadDict["state"]["reported"]["reedswitch"]))
        print("reported state: " + str(payloadDict["state"]["reported"]))

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")


## Variables para controlar entre que horas el AC puede activarse
acStartHour = 6
acEndHour = 18

class shadowCallbackContainer:
    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance

    ## shadowGet para ver el estado actual del documento shadow
    def shadowGet_Callback(self, payload,responseStatus,token):
        print("~~~~ shadowGet_Callback ~~~~")
        payloadDict = json.loads(payload)
        try:
            global acStartHour
            acStartHour = payloadDict["state"]["reported"]["acStartHour"]
            print("acStartHour: "+ acStartHour)
        except KeyError as error:
            print("acStartHour: 6")
        try:
            global acEndHour
            acEndHour = payloadDict["state"]["reported"]["acEndHour"]
            print("acEndHour: "+ acEndHour) 
        except KeyError as error:
            print("acEndHour: 18")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


    # Custom Shadow callback
    def customShadowCallback_Delta(self, payload, responseStatus, token):
        # payload is a JSON string ready to be parsed using json.loads(...)
        # in both Py2.x and Py3.x

	# Cuando se recibe un delta es porque el shadow fue actualizado por un usuario
	# y el dispositivo tiene que determinar que hacer con el valor del delta.
	# Por ejemplo, si el delta es un mensaje para ejecutar un comando, el raspberrpi debera
	# ejecutar un codigo extra en este punto. Si es abrir o cerrar una ventana, 
	# el rpi tiene que enviar la senal a un pin conectado a un relay. 

        print("~~~~ customShadowCallback_Delta ~~~~")
        payloadDict = json.loads(payload)
        deltaMessage = json.dumps(payloadDict["state"])
        print(deltaMessage)

        if payloadDict["state"]["waterpump"] == True:
            print("waterpump On")
            GPIO.output(waterpumpPin,0) #GPIO22 = 15 BOARD
        else:
            print("waterpump Off")
            GPIO.output(waterpumpPin,1) #0=activar el pin / 1=desactiva el pin

        print("Request to update the reported state...")
        newPayload = '{"state":{"reported":' + deltaMessage + '}}'
        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


## Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store",  dest="rootCAPath", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path",required=True)
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path", required=True)
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name", required=True)
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="ThingShadowEcho",help="Targeted client id", required=True)
parser.add_argument("-ri", "--refreshInterval", action="store", dest="refreshinterval", required=True, help="Refresh interval in Seconds")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId
refreshinterval = args.refreshinterval

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

## Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

## Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


## Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

## AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec


##AWS IoT
connected = False

## Connect to AWS IoT
while not connected:
    try:
        myAWSIoTMQTTShadowClient.connect()

       # Create a deviceShadow with persistent subscription
        deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)
        shadowCallbackContainer_Bot = shadowCallbackContainer(deviceShadowHandler)

       # Configura el callback cuando se hace la consulta del objecto shadow document
       # shadowGet_Callback se llama la primera vez que el programa inicia para 
       # obtener los valores de acStartHour y acEndHour del documento shadow. 
        deviceShadowHandler.shadowGet(shadowCallbackContainer_Bot.shadowGet_Callback,5)

       # Listen on deltas
        deviceShadowHandler.shadowRegisterDeltaCallback(shadowCallbackContainer_Bot.customShadowCallback_Delta)

        connected = True
        break
    except Exception as e:
       #TODO: Mejorar el manejo de excepciones.
        print("**** Error AWS MQTTShadowClient.connect(): "+repr(e))
        time.sleep(5)
        continue



sps30Serial = '4FBFC0FBE824FFEA'
#dht22H = 0.0
#dht22T = 0.0

## Esta funcion devuelve la hora actual del sistema para determinar si el AC se activa o no
def getHour():
   from datetime import datetime
   return int((((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[0])

## Definicion de callbacks para MQTT que corre en el host aws-rpi02
def on_message_acControlTopic_Callback(client, userdata, message):
   #print("Message Recieved: "+message.payload.decode())
   payload = json.loads(message.payload.decode())
   print("~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
   acOn = 0
   global acStartHour
   global acEndHour
   try:
      acStartHour = payload["acStartHour"]
      acEndHour = payload["acEndHour"]
      acOn = payload["acOn"]
      if repr(acOn) == "1":
         os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py a") ##Activa modo auto del AC
      if repr(acOn) == "0":
         os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##0 apaga el aire

   except KeyError as e:
      print("Exception: KeyError: ")

   print("acStartHour: " + repr(acStartHour))
   print("acEndHour: " + repr(acEndHour))
   print("acOn: " + repr(acOn))
   print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")


esp32LevelSwitch = 1 ##1 significa que el level switch esta abajo
def on_message_esp32LevelSwitch_Callback(client, userdata, message):
   #print("Message Recieved: "+message.payload.decode())
   print("~~~~ on_message_mqtt_esp32/levelwitch_topic_Callback ~~~~")
   try:
     payload = json.loads(message.payload.decode())
     print(client)
     print(userdata)
     global esp32LevelSwitch
     esp32LevelSwitch = payload
     print(esp32LevelSwitch)
   except json.decoder.JSONDecodeError as e:
     print("~~~~ JSONDecodeError ~~~~")
   print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")


broker_url = "192.168.4.202" #mosquitto docker corriendo en el raspberrypi
broker_port = 1883
mqttClient = mqtt.Client()
#mqttClient.on_connect = on_connect
#mqttClient.on_disconnect = on_disconnect
mqttClient.connect(broker_url, broker_port)
mqttClient.subscribe("acControlTopic", qos=1)
mqttClient.subscribe("esp32/levelswitch",qos=1)
mqttClient.message_callback_add("acControlTopic",on_message_acControlTopic_Callback)
mqttClient.message_callback_add("esp32/levelswitch",on_message_esp32LevelSwitch_Callback)
mqttClient.loop_start()

## Obtiene el Serial Number del RPi SoC
rpiSoCSerial = ""
with open('/home/pi/aws_iot/rpi-cpu-serial.json','r') as f:
   soc_json = json.load(f)
   rpiSoCSerial = soc_json['serial']
   f.close()



#Forever Loop
while True:
    ds18b20TemperatureC,null = read_ds18b20()
    ds18b20TemperatureC = round(ds18b20TemperatureC,1)

#    try:
#       dht22H = dht22.humidity
#       time.sleep(1)
#       dht22H = dht22.humidity ## Se lee dos veces la temp y humedad para permitir q la lectura del sensor se nivele
#       time.sleep(1)
#       dht22T = dht22.temperature
#       time.sleep(1)
#       dht22T = dht22.temperature
#    except RuntimeError:
#       print("*** No se puede leer DHT22! ***")
#    except OverflowError:
#       print("*** DHT22 OverflowError! ***")

    JSONPayload = ('{\"state\": { \"reported\": {')

    #Abrir el archivo para leer la informacion del SPS30
    with open('/home/pi/aws_iot/Sensirion/sps30-uart-3.0.0/sps30.json', 'r') as f:
        try:
             sps30_json = json.load(f)
             #print(sps30_json)

             if "error" in sps30_json:
                 print("SPS30 Error: ", sps30_json['error'])
                 JSONPayload = (JSONPayload + 
                                '\"sps30\": {'
                                        '\"error\":\"'+sps30_json['error']+'\",'
                                        '\"serial\":\"'+sps30Serial+'\"' #En cada actualizacion es necesario incluir
#el numero de serie del sensor sps30, porque la coleccion /thingCollection/yUp3qLUftKGGY01XdcL5/sps30 puede tener actualizaciones de cada sensor de polvo 
                                '},')
             else:
                 JSONPayload = (JSONPayload + 
                                '\"sps30\": {'
                                        '\"auto_clean_interval_days\":'+repr(sps30_json['auto_clean_interval_days'])+','
                                        '\"tps\":'+repr(sps30_json['tps'])+','
                                        #'\"serial\":\"'+sps30_json['serial']+'\",'
                                        '\"serial\":\"'+sps30Serial+'\",'
					'\"pm10.0\":'+ repr(sps30_json['pm10.0']) +','
                                        '\"nc10.0\":'+ repr(sps30_json['nc10.0'])+','
                                        '\"nc4.5\":'+ repr(sps30_json['nc4.5'])+','
                                        '\"pm2.5\":'+ repr(sps30_json['pm2.5'])+','
                                        '\"nc1.0\":'+ repr(sps30_json['nc1.0'])+','
                                        '\"nc2.5\":'+ repr(sps30_json['nc2.5'])+','
                                        '\"pm4.0\":'+ repr(sps30_json['pm4.0'])+','
                                        '\"nc0.5\":'+ repr(sps30_json['nc0.5'])+','
                                        '\"pm1.0\":'+ repr(sps30_json['pm1.0'])+','
                                        '\"error\":\"none\"'
                                '},')


        except json.decoder.JSONDecodeError as error:
             print("JSON Not defined json.decoder.JSONDecodeError: ", error)
             #json no definido
             JSONPayload = (JSONPayload + 
                                '\"sps30\": {'
                                        '\"error\":\"file not read\",'
                                        '\"serial\":\"'+sps30Serial+'\"'
                                '},')
        f.close()

    ds18b20_JSONPayload = ('{\"id\":' + repr(1)+','
                             '\"t\":' + repr(ds18b20TemperatureC)+
                           '}')

    #dht22_JSONPayload = ('{\"id\":' + repr(1)+','
    #                       '\"h\":' + repr(dht22H)+','
    #                       '\"t\":' + repr(dht22T)+
    #                     '}')

    sht31dT = round(sht31d.temperature,1)
    sht31dH = round(sht31d.relative_humidity,1)

    sht31d_JSONPayload = ('{\"id\":' + repr(1)+','
                            '\"t\":' + repr(sht31dT)+','
                            '\"h\":' + repr(sht31dH)+
                          '}')

    ds18b20_File = open("/home/pi/aws_iot/ds18b20.json","w")
    ds18b20_File.write(ds18b20_JSONPayload)
    ds18b20_File.close()

    #dht22_File = open("/home/pi/aws_iot/dht22.json","w")
    #dht22_File.write(dht22_JSONPayload)
    #dht22_File.close()

    #RaspberryPi CPU CORE Temp
    rpiSoCTemp = ""
    with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
      core_temp_json = json.load(f)
      #print(core_temp_json['CPUTemp'])
      rpiSoCTemp = repr(core_temp_json['CPUTemp'])
      f.close()

    rpiSoC_JSONPayload = ('{\"serial\":\"'+ rpiSoCSerial + '\",'
                            '\"cpuTemp\":'+rpiSoCTemp +
                          '}')


    sht31d_File = open("/home/pi/aws_iot/sht31d.json", "w")
    sht31d_File.write(sht31d_JSONPayload)
    sht31d_File.close()

    #esp32/levelswitch values:
    esp32LevelSwitchJSONPayload = ('{\"id\":' + repr(1)+','
                                     '\"value\":' + repr(esp32LevelSwitch)+
                                   '}')


    JSONPayload = (JSONPayload + '\"ds18b20\":' + ds18b20_JSONPayload + ',' +
                                 #'\"dht22\":' + dht22_JSONPayload + ',' +
                                 '\"rpiSoC\":' + rpiSoC_JSONPayload + ',' +
                                 '\"sht31d\":' + sht31d_JSONPayload + ',' +
                                 '\"esp32LevelSwitch\":'+ esp32LevelSwitchJSONPayload + '}}}')

    print(JSONPayload)

    try:
       deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
    except Exception as e:
        #Puede arrojar: AWSIoTPythonSDK.exception.AWSIoTExceptions.publishQueueDisabledException
        print("**** Error AWS IoT shadowUpdate: "+repr(e))
        continue


    ## Implementacion del control del AC
    ## Cuando la temperatura sube >= 27.5, activa modo DRY de AC
    currentHour = getHour()
    ## Primero se revisa si el AC puede activarse con base en las horas de actividad del AC
    print("acStartHour: "+repr(acStartHour))
    print("acEndHour: "+repr(acEndHour))
    print("currentHour: "+repr(currentHour))

    if currentHour >= acStartHour and currentHour <= acEndHour:
       if sht31dT >= 27.5: ##Max Temp
          print("\n~~~~ AC Turned On! ~~~~\n")
          os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py a") ##Activa modo auto del AC
       if sht31dT <= 23.5: ##Min Temp
          ## Cuando la temperatura <= 22 apaga el AC
          print("\n~~~~ AC Turned Off! ~~~~\n")
          os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##Apaga AC


    time.sleep(int(refreshinterval))



