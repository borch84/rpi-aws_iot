#!/bin/bash
ps -ef | grep push-button-gpiozero-read-ec.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/rpi-aws_iot/push-button-gpiozero-read-ec.py"; 
   python3 /home/pi/rpi-aws_iot/push-button-gpiozero-read-ec.py -pb 27 -fp /home/pi/rpi-aws_iot/ec100.json
fi