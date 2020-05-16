#!/usr/bin/env python3

from gpiozero import Button
from subprocess import check_call
from signal import pause

def button_callback():
    print("Hola!")

shutdown_btn = Button(27, hold_time=1)
shutdown_btn.when_held = button_callback

pause()