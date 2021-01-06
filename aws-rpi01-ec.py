#!/usr/bin/python3
from __future__ import print_function
#import sys 
import argparse

#LCD 16x2:
# import RPI_I2C_driver # not using when nextion is connected

#Atlas Scientific i2c implementation
from Atlas import atlas_i2c

"""
Para correr este programa: 

-fp /home/pi/rpi-aws_iot/ec100.json 

"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-fp", "--file_path",action="store", required=True, dest="file_path", help="EC Reading JSON File Path")


    args = parser.parse_args()
    file_path = args.file_path


    ec_device = atlas_i2c(address=100,bus=1,file_path=file_path,sensor_type='ec')  # creates the I2C port object, specify the address, bus and file path name to write the json object
    
    """mylcd = RPI_I2C_driver.lcd()
    mylcd.lcd_clear()
    mylcd.lcd_display_string("** High Corp **", 1)
    mylcd.lcd_display_string("Reading...", 2)
    """
    try:
        #print (device.query(sys.argv[1]),file=sys.stdout)
        ec_result = ec_device.query('r')
        print ("EC Value: "+ repr(ec_result)+" uS")
        """mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("EC: "+ repr(ec_result)+" uS", 2) """

    except Exception as e:
        print ("Exception: "+repr(e),file=sys.stderr)

if __name__ == '__main__':
    main()

