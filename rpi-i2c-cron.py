#RPi Pinouts

#I2C Pins 
#GPIO2 -> SDA
#GPIO3 -> SCL

#Import the Library Requreid 
import smbus
import time

import sys

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)


#Slave Address 
address = 0x05 #Esta es la direccion i2c del arduino que tiene conectado el infrarojo

def writeNumber(value):
    bus.write_byte(address, value)
    return -1

def readNumber():
    number = bus.read_byte_data(address, 1)
    return number
    
#while True:
#Receives the data from the User
#data = input("Enter the data to be sent : ")
#data_list = list(sys.argv[2])
#for i in data_list:
   #Sends to the Slaves 
writeNumber(int(ord(sys.argv[1])))
time.sleep(.1)

writeNumber(int(0x0A))

#End of the Script
