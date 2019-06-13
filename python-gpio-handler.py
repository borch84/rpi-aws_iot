#!/usr/bin/env python3

from gpiozero import DigitalInputDevice
from signal import pause

def reedswitch_closed():
	print("reed switch is closed!")

def reedswitch_opened(): 
	print("reed switch is opened!")

reedswitch = DigitalInputDevice(17,pull_up=True, bounce_time=1)

reedswitch.when_activated = reedswitch_closed

reedswitch.when_deactivated = reedswitch_opened

pause()