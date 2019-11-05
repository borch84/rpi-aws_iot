#!/usr/bin/env python3

import time
import argparse
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pin",action="store", required=True, dest="pin", help="Pin Relay Number")
parser.add_argument("-s", "--signal", action="store", required=True, dest="signal", help="[On|Off] signal")

args = parser.parse_args()
pin = int(args.pin)
signal= args.signal
GPIO.setup(pin,GPIO.OUT)

while True:
  if signal == "On":
    #print("Relay ON")
    GPIO.output(pin,0) #0 activa el pin Normally open
  else:
    #print("Relay OFF")
    GPIO.output(pin,1)  

