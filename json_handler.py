import json

def read_field(file_path, field):
  try:
    with open(file_path,'r') as f:
      purge_time_json = json.load(f)
      value = purge_time_json[field]
      f.close()
      return value
  except Exception as e:
      print("**** Exception reading json file: "+repr(e))
      return -1

def write_field(file_path,new_value,field):
  try:
    with open(file_path,'r') as f:
      json_data = json.load(f)
      f.close()
    json_data[field] = new_value
    with open(file_path,'w') as f:
      json.dump(json_data,f)
      f.close()
    return True
  except Exception as e:
      print("**** Exception writing json file: "+repr(e))
      return False