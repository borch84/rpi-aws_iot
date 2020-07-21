import RPI_I2C_driver
import argparse
import json
import time


parser = argparse.ArgumentParser()
parser.add_argument("-ec", "--ec",action="store", required=False, dest="ec_file", help="EC File Path Readings")
parser.add_argument("-ph", "--ph",action="store", required=False, dest="ph_file", help="PH File Path Readings")
parser.add_argument("-sht31d", "--sht31d",action="store", required=False, dest="sht31d_file", help="SHT31D File PAth Readings")

args = parser.parse_args()
ec_path = args.ec_file
ph_path = args.ph_file
sht31d_path = args.sht31d_file
mylcd = RPI_I2C_driver.lcd()


def getValue(path,sensor_type,unit):
    try:
      with open(path,'r') as f:
        json_file = json.load(f)
        value = repr(json_file[sensor_type])
        f.close()
        return "|"+ sensor_type +": " + value + unit
    except Exception as e:
        print("**** Excepcion: "+repr(e))
        return None

while True:
    mylcd.lcd_clear()
    lcd_message = ""
    if ec_path != None:
        ec = getValue(ec_path,'ec','uS')
        if ec != None:
            lcd_message += ec

    if ph_path != None:
        ph = getValue(ph_path,'ph','ph')
        if ph != None:
            lcd_message += ph

    if sht31d_path != None:
        t = getValue(sht31d_path,'t','C')
        if t != None:
            lcd_message += t
        h = getValue(sht31d_path,'h','%')
        if h != None:
            lcd_message += h


    for i in range(len(lcd_message)):
        mylcd.lcd_clear()
        mylcd.lcd_display_string(lcd_message[i:], 1)
        print(lcd_message[i:])
        time.sleep(1)

