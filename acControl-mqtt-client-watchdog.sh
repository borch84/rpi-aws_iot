#!/bin/bash
ps -ef | grep /home/pi/aws_iot/acControl-mqtt-client.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting acControl-mqtt-client.py"
   python3 /home/pi/aws_iot/acControl-mqtt-client.py -b 192.168.4.202 -t acControlTopic -ri 10
fi