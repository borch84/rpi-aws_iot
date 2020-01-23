import json
with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
   core_temp_json = json.load(f)
   print(core_temp_json['CPUTemp'])
   f.close()
