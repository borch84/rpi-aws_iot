import json

def getRPiCPUSerial():
    try:
      with open('/home/pi/aws_iot/rpi-cpu-serial.json','r') as f:
        soc_json = json.load(f)
        rpiSoCSerial = soc_json['serial']
        return rpiSoCSerial
        f.close()
    except Exception as e:
        print("**** Excepcion leyendo rpi-cpu-serial.json! ****"+repr(e))
        return None

def jsonpayload(rpiSoCSerial):
    try:
      with open('/home/pi/aws_iot/rpi-cpu-core-temp.log','r') as f:
        core_temp_json = json.load(f)
        #print(core_temp_json['CPUTemp'])
        rpiSoCTemp = repr(core_temp_json['CPUTemp'])
        f.close()
        rpiSoC_JSONPayload = ('\"rpiSoC\":' + '{\"serial\":\"'+ rpiSoCSerial + '\",'
                               '\"cpuTemp\":'+rpiSoCTemp +
                              '}')
        return rpiSoC_JSONPayload
    except Exception as e:
        print("**** Excepcion leyendo rpi-cpu-temp.log! ****"+repr(e))
        return None
