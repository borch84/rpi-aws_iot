from __future__ import print_function
import sys

from gpiozero import Button
from signal import pause

#LCD 16x2:
import RPI_I2C_driver

#Atlas Scientific i2c implementation
from Atlas import atlas_i2c

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-pb", "--push_button",action="store", required=True, dest="push_button", help="Push Button Pin Relay Number")
parser.add_argument("-fp", "--file_path",action="store", required=True, dest="file_path", help="EC Reading JSON File Path")

"""
-pb --push_button = 27
-fp --file_path = /home/pi/rpi-aws_iot/ec100.json
"""

args = parser.parse_args()
push_button = int(args.push_button)
file_path = args.file_path

device = atlas_i2c(address=100,bus=1,file_path=file_path) 
mylcd = RPI_I2C_driver.lcd()

def button_callback(channel):
    print("Button was pushed!")
    global mylcd
    global device
    mylcd.lcd_clear()
    mylcd.lcd_display_string("** High Corp **", 1)
    mylcd.lcd_display_string("Reading...", 2)
    try:
        ec = device.query('r')
        mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("EC: "+ repr(ec)+" uS", 2)

    except Exception as e:
        print ("Exception: "+repr(e),file=sys.stderr)
        mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("Error", 2)
    
read_ec_btn = Button(push_button, hold_time=1)
read_ec_btn.when_held = button_callback

pause()