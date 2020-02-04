
import paho.mqtt.client as mqtt
import json
import time

def on_message_acControlTopic_Callback(client, userdata, message):
   #print("Message Recieved: "+message.payload.decode())
   payload = json.loads(message.payload.decode())
   print("~~~~ on_message_mqtt_acControlTopic_Callback ~~~~")
   #acOn = 0
   #global acStartHour
   #global acEndHour
   try:
      acStartHour = payload["acStartHour"]
      acEndHour = payload["acEndHour"]
      acOn = payload["acOn"]

      print("acStartHour: " + repr(acStartHour))
      print("acEndHour: " + repr(acEndHour))
      print("acOn: " + repr(acOn))
      

      if repr(acOn) == "1":
         os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 1") ##Activa modo auto del AC
      if repr(acOn) == "0":
         os.system("/usr/bin/python3 /home/pi/aws_iot/rpi-i2c-cron.py 0") ##0 apaga el aire

   except KeyError as e:
      print("Exception: KeyError: ")

   print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")



#esp32LevelSwitch = 1 ##1 significa que el level switch esta abajo

def on_message_esp32LevelSwitch_Callback(client, userdata, message):
   #print("Message Recieved: "+message.payload.decode())
   print("~~~~ on_message_mqtt_esp32/levelwitch_topic_Callback ~~~~")
   try:
     payload = json.loads(message.payload.decode())
     #print(client)
     #print(userdata)
     #escribir el valor del esp32levelswitch en un archivo

     esp32LevelSwitchJSONPayload = ('\"esp32LevelSwitch\": {\"id\":' + repr(1)+','
                                     '\"value\":' + repr(payload)+
                                   '}')

     esp32LevelSwitchFile = open("/home/pi/aws_iot/esp32levelswitch.json", "w")
     esp32LevelSwitchFile.write(esp32LevelSwitchJSONPayload)
     esp32LevelSwitchFile.close()

     print(esp32LevelSwitchJSONPayload)

   except json.decoder.JSONDecodeError as e:
     print("~~~~ JSONDecodeError Exception! ~~~~")
   except Exception as e:
   	 print("~~~~ esp32levelswitch Exception: ")
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

while True:
	time.sleep(1) #dormir por 1 segundo