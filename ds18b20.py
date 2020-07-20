import os
import glob

def jsonpayload():
    base_dir = '/sys/bus/w1/devices/'
    try:
       device_folder = glob.glob(base_dir + '28*')[0]
       device_file = device_folder + '/w1_slave'
       f = open(device_file, 'r')
       lines = f.readlines()
       f.close()
       equals_pos = lines[1].find('t=')
       if equals_pos != -1:
         temp_string = lines[1][equals_pos+2:]
         temp_c = float(temp_string) / 1000.0
         #temp_f = temp_c * 9.0 / 5.0 + 32.0

         temp_c = round(temp_c,1)
         ds18b20_JSONPayload = ('{\"id\":' + repr(1)+','
                                             '\"t\":' + repr(temp_c) +
                                            '}')
         ds18b20_File = open("/home/pi/aws_iot/ds18b20.json","w")
         ds18b20_File.write(ds18b20_JSONPayload)
         ds18b20_File.close()
         return ds18b20_JSONPayload
         #return temp_c, temp_f

    except Exception as e:
       print("**** Error reading ds18b20 sensor! ****")
       print(e)
       return None

