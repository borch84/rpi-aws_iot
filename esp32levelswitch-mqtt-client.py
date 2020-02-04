
import paho.mqtt.client as mqtt
import json
import time
import argparse



def on_message_esp32LevelSwitch_Callback(client, userdata, message):
#print("Message Recieved: "+message.payload.decode())
  print("~~~~ on_message_mqtt_esp32/levelwitch_topic_Callback ~~~~")
  try:
    payload = json.loads(message.payload.decode())
    #print(client)
    #print(userdata)
    #escribir el valor del esp32levelswitch en un archivo

    global sensor_id
    esp32LevelSwitchJSONPayload = ('\"esp32LevelSwitch\": {\"id\":' + sensor_id +','
                                   '\"value\":' + repr(payload)+
                                 '}')

    esp32LevelSwitchFile = open("/home/pi/aws_iot/esp32levelswitch_"+ sensor_id +".json", "w")
    esp32LevelSwitchFile.write(esp32LevelSwitchJSONPayload)
    esp32LevelSwitchFile.close()

    print(esp32LevelSwitchJSONPayload)

  except json.decoder.JSONDecodeError as e:
    print("~~~~ JSONDecodeError Exception! ~~~~")
  except Exception as e:
    print("~~~~ esp32levelswitch Exception: ")
    print(e)

  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

## Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-id", "--sensor_id", action="store", dest="sensor_id", help="sensor id of esp32LevelSwitch", required=True)
parser.add_argument("-b", "--broker_url", action="store", dest="broker_url", help="broker_url", required=True)
parser.add_argument("-t", "--topic", action="store", dest="topic", help="esp32 level switch topic", required=True)


args = parser.parse_args()
broker_url = args.broker_url
topic = args.topic
sensor_id = args.sensor_id


#broker_url = "192.168.4.202" #mosquitto docker corriendo en el raspberrypi
broker_port = 1883
mqttClient = mqtt.Client()
#mqttClient.on_connect = on_connect
#mqttClient.on_disconnect = on_disconnect
mqttClient.connect(broker_url, broker_port)
#mqttClient.subscribe("esp32/levelswitch",qos=1)
#mqttClient.message_callback_add("esp32/levelswitch",on_message_esp32LevelSwitch_Callback)
mqttClient.subscribe(topic,qos=1)
mqttClient.message_callback_add(topic,on_message_esp32LevelSwitch_Callback)

mqttClient.loop_start()

while True:
	time.sleep(1) #dormir por 1 segundo