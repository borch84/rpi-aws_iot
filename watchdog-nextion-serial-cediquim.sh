#!/bin/bash
ps -ef | grep nextion-serial-cediquim.py| grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/rpi-aws_iot/nextion-serial-cediquim.py"; 
   python3 /home/pi/rpi-aws_iot/nextion-serial-cediquim.py
fi