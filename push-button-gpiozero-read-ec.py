from __future__ import print_function
import sys

from gpiozero import Button
from signal import pause

#LCD 16x2:
import RPI_I2C_driver

#Atlas Scientific i2c implementation
from Atlas import atlas_i2c

def button_callback(channel):
    print("Button was pushed!")
    device = atlas_i2c() 
    mylcd = RPI_I2C_driver.lcd()
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
    
read_ec_btn = Button(27, hold_time=1)
read_ec_btn.when_held = button_callback

pause()