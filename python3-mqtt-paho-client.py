import paho.mqtt.client as mqtt
import json

broker_url = "192.168.4.202"
broker_port = 1883

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code " (rc))

def on_disconnect(client, userdata, rc):
   print("Client Got Disconnected")

def on_message_acControlTopic_Callback(client, userdata, message):
   #print("Message Recieved: "+message.payload.decode())
   payload = json.loads(message.payload.decode())
   print("startHour: " + repr(payload["startHour"]))
   print("endHour: " + repr(payload["endHour"]))

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(broker_url, broker_port)

client.subscribe("acControlTopic", qos=1)
client.message_callback_add("acControlTopic",on_message_acControlTopic_Callback)

#client.publish(topic="startHour", payload="TestingPayload", qos=1, retain=False)

client.loop_forever()
