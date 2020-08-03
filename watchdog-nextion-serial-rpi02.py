#!/bin/bash
ps -ef | grep /home/pi/aws_iot/nextion-serial-rpi02.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/aws_iot/nextion-serial-rpi02.py"; 
   /home/pi/aws_iot/nextion-serial-rpi02.py
fi