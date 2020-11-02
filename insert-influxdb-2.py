#!/usr/bin/python3
import json
import argparse
from influxdb import InfluxDBClient

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file",action="store", required=True, dest="file", help="Measurement JSON File")
parser.add_argument("-m", "--measurement",action="store", required=True, dest="measurement", help="InfluxDB Measurement")
parser.add_argument("-tk", "--tag_key",action="store", required=True, dest="tag_key", help="Tag Key")
parser.add_argument("-tv", "--tag_value",action="store", required=True, dest="tag_value", help="Tag Value")
parser.add_argument("-k", "--keys",action="store", required=True, dest="keys", help="List of Keys' names in the measurement")  

args = parser.parse_args()
file_path = args.file
measurement = args.measurement
tag_key = args.tag_key
tag_value = args.tag_value
fields = {}

try:
  with open(file_path,"r") as f:
    data = f.read()
  f.close()
  json_data = json.loads(data)
  for k in args.keys.split(","):
    fields[k]=json_data[k]
  new_data = [
    {
        'measurement': measurement,
        'tags': {tag_key: tag_value},
        'fields': fields
    }
  ]
  print(new_data)
  client = InfluxDBClient(host='localhost',port=8086,database='iotdb')
  client.write_points(new_data)
  client.close()
  print("write OK")
except Exception as e:
  print ("Exception: "+repr(e))

