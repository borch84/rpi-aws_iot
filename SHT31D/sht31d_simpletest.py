#pip3 install adafruit-circuitpython-sht31d --user

import time
import board
import busio
import adafruit_sht31d

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

loopcount = 0
while True:
	print("\nTemperature: %0.1f C" % sensor.temperature)
	print("Humidity: %0.1f %%" % sensor.relative_humidity)
	time.sleep(5)
	#loopcount += 1
	#cada 10 pasadas se activa un heater interno del sensor
	#if loopcount == 10:
	#	loopcount = 0
	#	sensor.heater = True
	#	print("Sensor Header status =", sensor.heater)
	#	time.sleep(1)
	#	sensor.heater = False
	#	print("Sensor Heater status =", sensor.heater)
