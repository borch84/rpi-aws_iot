import json

def read_purge_time_json(file_path):
  try:
    with open(file_path,'r') as f:
      purge_time_json = json.load(f)
      value = purge_time_json['sec']
      f.close()
      return value
  except Exception as e:
      print("**** Excepcion reading purge_time.json! ****"+repr(e))
      return -1

def write_purge_time_json(file_path,new_value):
  try:
    with open(file_path,'w') as f:
      json = "{\"sec\":"+ str(new_value) +"}" 
      f.write(json)
      f.close()
      return True
  except Exception as e:
      print("**** Excepcion writing purge_time.json! ****"+repr(e))
      return False