#!/bin/bash
ps -ef | grep aws-thing-shadow3.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/aws_iot/aws-ec-thing-shadow.py"; 
   python3 /home/pi/aws_iot/aws-thing-shadow3.py -e a3s9lktlbmjbgn-ats.iot.us-east-1.amazonaws.com -r /home/pi/aws_iot/aws-root-ca.pem -c /home/pi/aws_iot/rpi-cediquim-certs/97b1fdbd66-certificate.pem.crt -k /home/pi/aws_iot/rpi-cediquim-certs/97b1fdbd66-private.pem.key -n rpi-cediquim -id rpi-cediquim -ri 120 -as /home/pi/aws_iot/rpi-cediquim-active-sensors.json 2>&1 | tee /home/pi/aws_iot/aws-ec-thing-shadow-$(date +%F-%H-%M).log
fi
