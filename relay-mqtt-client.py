import paho.mqtt.client as mqtt
import json
import time
import argparse
import RPi.GPIO as GPIO
from utils import getJSONValues
from threading import Timer

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def stop_timer(relay_pin):
    GPIO.output(relay_pin,1) 

def on_message_relayControlTopic_Callback(client, userdata, message):
    print("\n~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
    try:
      payload = json.loads(message.payload.decode())
      state = payload['state']
      if state == "on":
        pin = int(payload['relay_pin'])
        print(pin)
        minute = int(payload['minute'])
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0) #0 activa el pin Normally open
        timer1 = Timer(minute*60,stop_timer,args=(pin,))
        timer1.start()

      if state == "off":
        pin = int(payload['relay_pin'])
        print(pin)
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,1)
    except Exception as e:
      print(repr(e))
    

## Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--broker", action="store", dest="broker", help="broker url", required=False)
parser.add_argument("-bp", "--broker_port", action="store", dest="broker_port", help="broker port", required=False)
parser.add_argument("-t", "--topic", action="store", dest="topic", help="Relay Control Topic", required=False)
parser.add_argument("-ri", "--refreshInterval", action="store", dest="refresh_interval", required=False, help="Refresh interval in Seconds")

args = parser.parse_args()

broker, broker_port, topic, refresh_interval = getJSONValues('/home/pi/aws_iot/relayControl.json',['broker', 'broker_port', 'topic', 'refresh_interval'])

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
mqttClient.message_callback_add(topic,on_message_relayControlTopic_Callback)
mqttClient.reconnect_delay_set(min_delay=1, max_delay=120)

mqttClient.loop_start()

while True:
    print("\n~~~~~~~~~~~ Relay Control ~~~~~~~~~~~~~~")
    time.sleep(refresh_interval)
