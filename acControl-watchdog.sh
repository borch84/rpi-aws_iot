#!/bin/bash
ps -ef | grep /home/pi/aws_iot/acControl.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting acControl-mqtt-client.py"
   python3 /home/pi/aws_iot/acControl.py -ri 10
fi