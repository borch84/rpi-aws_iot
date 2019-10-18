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
import Adafruit_DHT
dht22_sensor_type = Adafruit_DHT.DHT22
dht22_sensor_pin = 19

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

old_humidity = 0
humidity = 0

old_temp = 0
temp = 0

def read_temp_ds18b20_raw():
    f = open(device_file, 'r')
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


from gpiozero import DigitalInputDevice
from gpiozero import OutputDevice
#from gpiozero import LED

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

#waterpump = DigitalOutputDevice(22,True,False)
#waterpump = LED(22)
waterpump =  OutputDevice(22)

reedswitch.when_activated = reedswitch_closed

reedswitch.when_deactivated = reedswitch_opened

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

        if payloadDict["state"]["windowOpen"] == True:
            print("waterpump On")
            waterpump.on()
        else:
            print("waterpump Off")
            waterpump.off()

        print("Request to update the reported state...")
        newPayload = '{"state":{"reported":' + deltaMessage + '}}'
        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
        print("Sent.")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="ThingShadowEcho",
                    help="Targeted client id")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

connected = False


# Connect to AWS IoT

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
while True:
    temp,null = read_ds18b20()
    temp = round(temp,1)
    if old_temp != temp:
    #if (abs(old_temp - temp) > 1 ): 
        print('**** Updating temperature value ****')
        JSONPayload = '{"state":{"reported":{"temp":'+repr(temp)+'}}}'
        print(JSONPayload)
        old_temp = temp
        deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)

    humidity, null = Adafruit_DHT.read_retry(dht22_sensor_type,dht22_sensor_pin)
    humidity = round(humidity,1)
    if old_humidity != humidity:
    #if (abs(old_humidity - humidity) > 1):
        print('**** Updating humidity value ****')
        JSONPayload = '{"state":{"reported":{"humidity":'+repr(humidity)+'}}}'
        print(JSONPayload)
        old_humidity = humidity
        deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)

    if reedswitch_state != old_reedswitch_state:
        print('**** Updating reedswith reported stated ****')
        if reedswitch_state:
            JSONPayload = '{"state":{"reported":{"reedswitch":true}}}'
        else:
            JSONPayload = '{"state":{"reported":{"reedswitch":false}}}'
        old_reedswitch_state = reedswitch_state
        deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
    time.sleep(10)
