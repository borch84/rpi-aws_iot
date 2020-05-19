#!/bin/bash
ps -ef | grep push-button-gpiozero-gpiozero-purge.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/rpi-aws_iot/push-button-gpiozero-purge.py"; 
   python3 /home/pi/rpi-aws_iot/push-button-gpiozero-purge.py -pb 27 -fp /home/pi/rpi-aws_iot/ec100.json -sp 4 -pp 17 -s 2
fi