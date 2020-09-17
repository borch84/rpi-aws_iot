#!/usr/bin/env python3

import time
import argparse
import RPi.GPIO as GPIO
import time_purge_handler_file

GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pin",action="store", required=True, dest="pin", help="Pin Relay Number")
parser.add_argument("-s", "--seconds", action="store", required=False, dest="seconds", help="Number of seconds the pin should be On")
parser.add_argument("-j", "--purge_json_file",action="store", required=False, dest="json", help="JSON Purge Time File")


args = parser.parse_args()
pin = int(args.pin)
json = args.json
if (json != None):
    seconds = (time_purge_handler_file.read_purge_time_json(json, 'min')) * 60
else:
    seconds = args.seconds



""" El numero de pin corresponde al pin del board, por ejemplo:
https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
BOARD = BCM
pin15 = gpio22
pin16 = gpio23
pin7 = gpio4 """

GPIO.setup(pin,GPIO.OUT)
GPIO.output(pin,0) #0 activa el pin Normally open
time.sleep(int(seconds))
GPIO.output(pin,1)

