from __future__ import print_function
import time
import sys 

import argparse
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

#LCD 16x2:
import RPI_I2C_driver

#Atlas Scientific i2c implementation
from Atlas import atlas_i2c

"""
Para correr este programa: python3 ec100.py -sp 4 -pp 17 -s 3 -maxec 0

-sp --solenoide_pin = 4
-pp --pump_pin = 17
-s --seconds
-maxec

"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-sp", "--solenoide_pin",action="store", required=True, dest="solepin", help="BCM Solenoide Pin Relay Number")
    parser.add_argument("-pp", "--pump_pin",action="store", required=True, dest="pumppin", help="BCM Pump Pin Relay Number")
    parser.add_argument("-s", "--seconds", action="store", required=True, dest="seconds", help="Number of seconds the pin should be On")
    parser.add_argument("-maxec", "--maxec",action="store", required=True, dest="maxec", help="Upper EC Value")

    args = parser.parse_args()
    sole_pin = int(args.solepin)
    pump_pin = int(args.pumppin)
    timeout_seconds = int(args.seconds)
    maxec = int(args.maxec)

    ec_device = atlas_i2c(address=100,bus=1,file_path="ec100.json")  # creates the I2C port object, specify the address, bus and file path name to write the json object
    mylcd = RPI_I2C_driver.lcd()
    mylcd.lcd_clear()
    mylcd.lcd_display_string("** High Corp **", 1)
    mylcd.lcd_display_string("Reading...", 2)

    try:
        #print (device.query(sys.argv[1]),file=sys.stdout)
        ec_result = ec_device.query('r')
        mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("EC: "+ repr(ec_result)+" uS", 2)
        if ec_result >= maxec: #upper maximum EC level
            print ("EC Value: "+ repr(ec_result)+" uS")
            print ("~~~~ Abre el soleoinde y desactiva Bomba ~~~~")
            GPIO.setup(sole_pin,GPIO.OUT)
            GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
            GPIO.setup(pump_pin,GPIO.OUT)
            GPIO.output(pump_pin,0) # 0 signal value activates relay pin
            time.sleep(int(timeout_seconds))
            GPIO.output(sole_pin,1)
            GPIO.output(pump_pin,1)

    except Exception as e:
        print ("Exception: "+repr(e),file=sys.stderr)



if __name__ == '__main__':
    main()

