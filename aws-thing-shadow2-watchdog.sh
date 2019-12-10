#!/bin/bash
ps -ef | grep /home/pi/aws_iot/aws-thing-shadow2.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/aws_iot/aws-thing-shadow2.py"; 
   /home/pi/aws_iot/comando-aws-thing-shadow2.py.sh
fi
