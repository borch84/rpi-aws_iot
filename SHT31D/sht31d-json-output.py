import time
import board
import busio
import adafruit_sht31d

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

print("{\"sensorid\":1, \"t\": %0.1f," %sensor.temperature)
print("\"h\": %0.1f}" % sensor.relative_humidity)
#print("}")
