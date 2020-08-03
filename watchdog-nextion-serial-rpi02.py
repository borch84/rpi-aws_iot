#!/bin/bash
pgrep nextion-serial-rpi02.py
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/aws_iot/nextion-serial-rpi02.py"; 
   python3 /home/pi/aws_iot/nextion-serial-rpi02.py
fi