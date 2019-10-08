#!/usr/bin/env python3

from gpiozero import Button
from subprocess import check_call
from signal import pause

def reboot():
    check_call(['sudo', 'reboot'])

shutdown_btn = Button(27, hold_time=3)
shutdown_btn.when_held = reboot

pause()