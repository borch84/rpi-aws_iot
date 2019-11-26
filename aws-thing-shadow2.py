#!/usr/bin/env python3
'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/html/index.html#module-AWSIoTPythonSDK.core.shadow.deviceShadow

 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
import argparse

import os
import glob
import time
#import sys

##Pronto voy a eliminar el DHT22 para usar solo Sensirion SHT31D
## https://github.com/adafruit/Adafruit_CircuitPython_DHT
import adafruit_dht
dht22 = adafruit_dht.DHT22(19)


##RPi.GPIO
##Para la activacion de los relays, se va a implementar la libreria RPi.GPIO porque permite el acceso concurrent $
import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#RPi.GPIO la bomba esta conectado al pin 15 = GPIO22
GPIO.setup(22, GPIO.OUT)
GPIO.output(22,1) #1=apaga la bomba


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
    print("reed switch is closed!")
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
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        #print("reported reedswitch state: " + str(payloadDict["state"]["reported"]["reedswitch"]))
        print("reported state: " + str(payloadDict["state"]["reported"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")


class shadowCallbackContainer:
    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance

    # Custom Shadow callback
    def customShadowCallback_Delta(self, payload, responseStatus, token):
        # payload is a JSON string ready to be parsed using json.loads(...)
        # in both Py2.x and Py3.x

	# Cuando se recibe un delta es porque el shadow fue actualizado por un usuario
	# y el dispositivo tiene que determinar que hacer con el valor del delta.
	# Por ejemplo, si el delta es un mensaje para ejecutar un comando, el raspberrpi debera
	# ejecutar un codigo extra en este punto. Si es abrir o cerrar una ventana, 
	# el rpi tiene que enviar la senal a un pin conectado a un relay. 

        print("Received a delta message:")
        payloadDict = json.loads(payload)
        deltaMessage = json.dumps(payloadDict["state"])
        print(deltaMessage)

        if payloadDict["state"]["waterpump"] == True:
            print("waterpump On")
            GPIO.output(15,0) #GPIO22 = 15 BOARD
        else:
            print("waterpump Off")
            GPIO.output(15,1) #0=activar el pin / 1=desactiva el pin

        print("Request to update the reported state...")
        newPayload = '{"state":{"reported":' + deltaMessage + '}}'
        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
        print("Sent.")


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

       # Listen on deltas
        deviceShadowHandler.shadowRegisterDeltaCallback(shadowCallbackContainer_Bot.customShadowCallback_Delta)

        connected = True
        break
    except Exception as e:
       #TODO: Mejorar el manejo de excepciones.
        print("**** Error: "+repr(e))
        time.sleep(5)
        continue



# Loop forever
sps30Serial = '4FBFC0FBE824FFEA'

while True:
    ds18b20TemperatureC,null = read_ds18b20()
    ds18b20TemperatureC = round(ds18b20TemperatureC,1)

    try:
       dht22H = dht22.humidity
       time.sleep(1)
       dht22H = dht22.humidity ## Se lee dos veces la temp y humedad para permitir q la lectura del sensor se nivele
       time.sleep(1)
       dht22T = dht22.temperature
       time.sleep(1)
       dht22T = dht22.temperature
    except RuntimeError:
       print("*** No se puede leer DHT22! ***")

    JSONPayload = ('{\"state\": {')

    #Abrir el archivo para leer la informacion del SPS30
    with open('Sensirion/sps30-uart-3.0.0/sps30.json', 'r') as f:
        try:
             sps30_json = json.load(f)
             #print(sps30_json)

             if "error" in sps30_json:
                 print("SPS30 Error: ", sps30_json['error'])
                 JSONPayload = (JSONPayload + '\"reported\": {'
                                '\"sps30\": {'
                                        '\"error\":\"'+sps30_json['error']+'\",'
                                        '\"serial\":\"'+sps30Serial+'\"' #En cada actualizacion es necesario incluir
#el numero de serie del sensor sps30, porque la coleccion /thingCollection/yUp3qLUftKGGY01XdcL5/sps30 puede tener actualizaciones de cada sensor de polvo 
                                '},')
             else:
                 JSONPayload = (JSONPayload + '\"reported\": {'
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
             JSONPayload = (JSONPayload + '\"reported\": {'
                                '\"sps30\": {'
                                        '\"error\":\"file not read\",'
                                        '\"serial\":\"'+sps30Serial+'\"'
                                '},')
        f.close()

    JSONPayload = (JSONPayload + '\"ds18b20\": {'
        				'\"id\":' + repr(1)+','
        				'\"t\":' + repr(ds18b20TemperatureC)+
      					'},'
      				'\"dht22\": {'
        				'\"id\":'+ repr(1)+','
        				'\"h\":' + repr(dht22H)+','
        				'\"t\":' + repr(dht22T)+
      				'},'
      				'\"sht31d\": {'
        				'\"id\":' + repr(1)+','
        				'\"t\":' + repr(round(sht31d.temperature,1))+','
        				'\"h\":' + repr(round(sht31d.relative_humidity,1))+
      				'}'
    			'}'
  		    '}'
		'}')

    print(JSONPayload)

    try:
       deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
    except Exception as e:
        #Puede arrojar: AWSIoTPythonSDK.exception.AWSIoTExceptions.publishQueueDisabledException
        print("**** Error: "+repr(e))
        continue

    time.sleep(int(refreshinterval))

