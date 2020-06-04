from __future__ import print_function
import io  # used to create file streams
import fcntl  # used to access I2C parameters like addresses
import time  # used for sleep delay and timestamps
import string  # helps parse strings
import sys

# Borch - Codigo adaptado para python3

class atlas_i2c:
    long_timeout = 5  # the timeout needed to query readings and calibrations
    short_timeout = 5  # timeout for regular commands
    default_bus = 1  # the default bus for I2C on the newer Raspberry Pis,
                     #certain older boards use bus 0
    default_address = 100  # the default address for the EC sensor
    device_file_path = "ec100.json" #

    def __init__(self, address=default_address, bus=default_bus,file_path=device_file_path):
        # open two file streams, one for reading and one for writing
        # the specific I2C channel is selected with bus
        # it is usually 1, except for older revisions where its 0
        # wb and rb indicate binary read and write
        self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)

        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)
        self.device_file_path = file_path

    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)

    def write(self, string):
        # appends the null character and sends the string over I2C
        string += "\00"
        byte_object = str.encode(string) #En python3 hay que convertir el string a byte para enviarlo como comando
        #self.file_write.write(string) #Para python2
        self.file_write.write(byte_object)

    def read(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C,
        #then parses and displays the result

        res = self.file_read.read(num_of_bytes)  # read from the board

        str_res = res.decode() #Como el codigo lo estamos corriendo en python3, hay que hacer decode primero del objecto bytes a string

        #response = list(filter(lambda x: x != '\x00', res)) #Para python2
        response = list(filter(lambda x: x != '\x00', str_res)) #El filter en python3 regresa un objeto iterable, not una list. Sin embargo list(iterable) convierte el objecto iterable en una lista, y la lista es subscriptable https://stackoverflow.com/questions/15876259/typeerror-filter-object-is-not-subscriptable

        # remove the null characters to get the response
        if(ord(response[0]) == 1):  # if the response isnt an error
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            # change MSB to 0 for all received characters except the first
            #and get a list of characters
            # NOTE: having to change the MSB to 0 is a glitch in the raspberry
            #pi, and you shouldn't have to do this!
            # convert the char list to a string and returns it
            device_file = open(self.device_file_path, "w")
            str_ec = ''.join(char_list)
            #print(str_ec)
            device_file.write("{\"status\":\"OK\",\"ec\":"+str_ec+"}")
            device_file.close()
            return float(str_ec)
        else:
            #print("{\"status\":\"ER\",\"code\":" + str(ord(response[0]))+"}",file=sys.stderr)
            device_file = open(self.device_file_path, "w")
            device_file.write("{\"status\":\"ER\",\"code\":" + str(ord(response[0]))+"}")
            device_file.close()
            #sys.exit(ord(response[0]))
            return None

    def query(self, string):
        # write a command to the board, wait the correct timeout,
        #and read the response
        self.write(string)

        # the read and calibration commands require a longer timeout
        if((string.upper().startswith("R")) or (string.upper().startswith("CAL"))):
            time.sleep(self.long_timeout)
        elif((string.upper().startswith("SLEEP"))):
            return "sleep mode"
        else:
            time.sleep(self.short_timeout)

        return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()