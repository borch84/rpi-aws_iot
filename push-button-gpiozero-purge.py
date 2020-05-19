from __future__ import print_function
import sys

from gpiozero import Button
from signal import pause
import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-sp", "--solenoide_pin",action="store", required=True, dest="solepin", help="BCM Solenoide Pin Relay Number")
parser.add_argument("-pp", "--pump_pin",action="store", required=True, dest="pumppin", help="BCM Pump Pin Relay Number")
parser.add_argument("-pb", "--push_button",action="store", required=True, dest="push_button", help="Push Button Pin Relay Number")
parser.add_argument("-s", "--seconds", action="store", required=True, dest="seconds", help="Number of seconds the pin should be On")
parser.add_argument("-fp", "--file_path",action="store", required=True, dest="file_path", help="EC Reading JSON File Path")

"""
-sp --solenoide_pin = 4
-pp --pump_pin = 17
-pb --push_button = 27
"""

args = parser.parse_args()
sole_pin = int(args.solepin)
pump_pin = int(args.pumppin)
push_button = int(args.push_button)
timeout_seconds = int(args.seconds)
file_path = args.file_path


GPIO.setup(sole_pin,GPIO.OUT)
GPIO.setup(pump_pin,GPIO.OUT)

#LCD 16x2:
import RPI_I2C_driver

#Atlas Scientific i2c implementation
from Atlas import atlas_i2c

device = atlas_i2c(address=100,bus=1,file_path=file_path) 
mylcd = RPI_I2C_driver.lcd()

def button_callback(channel):
    print("Button was pushed!")
    global mylcd
    global device
    global timeout_seconds
    global sole_pin
    global pump_pin

    mylcd.lcd_clear()
    mylcd.lcd_display_string("** High Corp **", 1)
    mylcd.lcd_display_string("Reading...", 2)
    try:
        ec = device.query('r')
        mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("EC: "+ repr(ec)+" uS", 2)
        GPIO.output(sole_pin,0) # 0 signal value activates relay pin            
        GPIO.output(pump_pin,0) # 0 signal value activates relay pin
        time.sleep(int(timeout_seconds))
        GPIO.output(sole_pin,1)
        GPIO.output(pump_pin,1)

    except Exception as e:
        print ("Exception: "+repr(e),file=sys.stderr)
        mylcd.lcd_clear()
        mylcd.lcd_display_string("** High Corp **", 1)
        mylcd.lcd_display_string("Error", 2)
    
read_ec_btn = Button(push_button, hold_time=1)
read_ec_btn.when_held = button_callback

pause()