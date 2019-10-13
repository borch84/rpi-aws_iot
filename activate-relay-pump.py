#!/usr/bin/env python3

import time
import argparse
from gpiozero import OutputDevice

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pin",action="store", required=True, dest="pin", help="Pin Relay Number")
parser.add_argument("-s", "--seconds", action="store", required=True, dest="seconds", help="Number of seconds the pin should be On")

args = parser.parse_args()
pin = args.pin
seconds = args.seconds

#if not args.pin and not args.second:
#    parser.error("Missing PIN number and SECONDS")
#    exit(2)

waterpump =  OutputDevice(pin)
waterpump.on()
time.sleep(int(seconds))
waterpump.off()


