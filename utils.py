import json
import subprocess

def getJSONValues(file,list_fields):
  fields_values = []
  try:
    with open(file,'r') as f:
      json_data = json.load(f)
      f.close()
    for field in list_fields:
      fields_values.append(json_data[field])
    return fields_values
  except Exception as e:
    print("getJSONValues Exception: "+repr(e))
    return None

def save_acControl(file_path,new_json):
  print("save ac control")
  print(new_json)
  try:
    with open(file_path,'r') as f:
      json_data = json.load(f)
      f.close()

    for key in new_json.keys():
      json_data[key] = new_json[key]

    with open(file_path,'w') as f:
      json.dump(json_data,f)
      f.close()
    
    with open(json_data['crontab_file'],'w') as f:
      if new_json['enabled']:
        f.write(json_data['crontab_content'])
      else:
        f.write("#"+json_data['crontab_content'])
      f.close()
    subprocess.run(["sudo", "cp", json_data['crontab_file'], "/etc/cron.d/"]) 
  except Exception as e:
      print("**** Exception save_acControl: "+repr(e))