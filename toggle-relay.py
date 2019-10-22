#!/usr/bin/env python3

import time
import argparse
from gpiozero import DigitalOutputDevice

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pin",action="store", required=True, dest="pin", help="Pin Relay Number")
parser.add_argument("-s", "--signal", action="store", required=True, dest="signal", help="[On|Off] signal")

args = parser.parse_args()
pin = args.pin
signal= args.signal


relaypin =  DigitalOutputDevice(pin,False,False)
while True:
  if signal == "On":
    #print("Relay ON")
    relaypin.on()
  else:
    #print("Relay OFF")
    relaypin.off()


