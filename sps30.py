import json
def jsonpayload():
  #sps30_JSONPayload = ""
  #Abrir el archivo para leer la informacion del SPS30
  try:
    f = open('/home/pi/aws_iot/Sensirion/sps30-uart-3.0.0/sps30.json', 'r') 
    sps30_JSONPayload = f.read()
    sps30_JSONPayload = '\"sps30\": ' + sps30_JSONPayload
    f.close()
    return sps30_JSONPayload
  except json.decoder.JSONDecodeError as error:
    print("**** SPS30 Error Log **** JSON Not defined json.decoder.JSONDecodeError: ", error)
    f.close()
    return None
  except Exception as e:
    print("**** sps30.py Exception: ",e)
    return None
