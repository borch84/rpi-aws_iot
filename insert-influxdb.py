#!/usr/bin/python3
import json
import argparse
from influxdb import InfluxDBClient

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file",action="store", required=True, dest="file", help="Measurement JSON File")
parser.add_argument("-m", "--measurement",action="store", required=True, dest="measurement", help="InfluxDB Measurement")
parser.add_argument("-s", "--sensor_id",action="store", required=True, dest="sensor_id", help="Sensor ID")
parser.add_argument("-l", "--label",action="store", required=True, dest="label", help="Field label name in the measurement")  

args = parser.parse_args()
file_path = args.file
measurement = args.measurement
sensor_id = args.sensor_id
label = args.label

client = InfluxDBClient(host='localhost',port=8086)
client.switch_database('iotdb')
try:
    with open(file_path,"r") as file:
        data = file.read()
    file.close()
    json_data = json.loads(data)
    if not (json_data.get("status") is None):
      if json_data["status"] == "OK":
        json_body = [
          {
          "measurement": measurement,
          "fields":
              {
                "id": sensor_id,
                label: json_data[label]
              }
          }
        ]
        client.write_points(json_body)
        client.close()
        print("write OK")
    else:
        json_body = [
          {
          "measurement": measurement,
          "fields":
              {
                "id": sensor_id,
                label: json_data[label]
              }
          }
        ]
        client.write_points(json_body)
        client.close()
        print("write OK")

except Exception as e:
    print ("Exception: "+repr(e))