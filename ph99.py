#!/usr/bin/python3
from __future__ import print_function
import time
import sys 
import argparse

#LCD 16x2:
# import RPI_I2C_driver # not using when nextion is connected

#Atlas Scientific i2c implementation
from Atlas import atlas_i2c

"""
Este script lee el sensor de ph Ezo de Atlas Scientific

"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-fp", "--file_path",action="store", required=True, dest="file_path", help="Ph Reading JSON File Path")


    args = parser.parse_args()
    file_path = args.file_path

    ph_device = atlas_i2c(address=99,bus=1,file_path=file_path,sensor_type='ph')  # creates the I2C port object, specify the address, bus and file path name to write the json object
    
    """mylcd = RPI_I2C_driver.lcd()
    mylcd.lcd_clear()
    mylcd.lcd_display_string("** High Corp **", 1)
    mylcd.lcd_display_string("Reading...", 2)
    """
    try:
        ph_result = ph_device.query('r')
        print ("Ph Value: "+ repr(ph_result)+" ph")
        """mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("EC: "+ repr(ec_result)+" uS", 2) """

    except Exception as e:
        print ("Exception: "+repr(e),file=sys.stderr)


if __name__ == '__main__':
    main()

