#!/usr/bin/env python3

import time
import argparse
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pin",action="store", required=True, dest="pin", help="Pin Relay Number")
parser.add_argument("-s", "--seconds", action="store", required=True, dest="seconds", help="Number of seconds the pin should be On")

args = parser.parse_args()
pin = int(args.pin)
seconds = args.seconds

//El numero de pin corresponde al pin del board, por ejemplo:
//pin15 = gpio22
//pin16 = gpio23
//En este caso se usa el numero de pin 15 para activar la bomba
GPIO.setup(pin,GPIO.OUT)
GPIO.output(pin,0) #0 activa el pin Normally open
time.sleep(int(seconds))
GPIO.output(pin,1)

