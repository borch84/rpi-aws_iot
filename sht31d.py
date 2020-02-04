##Sensirion SHT31D
import board
import busio #https://circuitpython.readthedocs.io/en/latest/shared-b$
import adafruit_sht31d
i2c = busio.I2C(board.SCL, board.SDA)
#https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity$
sht31d = adafruit_sht31d.SHT31D(i2c)


def jsonpayload():
    try:
      sht31dT = round(sht31d.temperature,1)
      sht31dH = round(sht31d.relative_humidity,1)
      sht31d_JSONPayload = ('{\"id\":' + repr(1)+','
                              '\"t\":' + repr(sht31dT)+','
                              '\"h\":' + repr(sht31dH)+
                            '}')
      sht31d_File = open("/home/pi/aws_iot/sht31d.json", "w")
      sht31d_File.write(sht31d_JSONPayload)
      sht31d_File.close()
      return sht31d_JSONPayload, sht31dT, sht31dH
    except RuntimeError as e:
      print("**** RuntimeError: CRC Mismatch! ****");
      return None
