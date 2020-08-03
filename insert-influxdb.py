#!/usr/bin/python3
import json
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost',port=8086)
client.switch_database('iotdb')
try:
    with open("/home/pi/aws_iot/ph99.json","r") as ph_file:
        ph_data = ph_file.read()
    ph_file.close()
    ph_json = json.loads(ph_data)
    ph_JSONPayload = ""
    if ph_json["status"] == "OK":
      json_body = [
        {
        "measurement": "ph99",
        "fields":
            {
              "id": "99",
              "ph": ph_json["ph"]
            }
        }
      ]
      client.write_points(json_body)
      client.close()
except Exception as e:
    print ("Ph Exception: "+repr(e))