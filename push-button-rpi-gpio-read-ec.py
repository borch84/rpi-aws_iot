from __future__ import print_function
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import sys


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
    
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 27 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(27,GPIO.RISING,callback=button_callback,bouncetime=700) # Setup event on pin 10 rising edge
message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up