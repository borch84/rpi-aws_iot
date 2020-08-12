#!/bin/bash
ps -ef | grep /home/pi/aws_iot/aws-thing-shadow3.py | grep -v grep
if [ $? -eq 1 ]; then 
   date
   echo "Process not running, restarting /home/pi/aws_iot/aws-thing-shadow3.py"; 
   python3 /home/pi/aws_iot/aws-thing-shadow3.py -e a3s9lktlbmjbgn-ats.iot.us-east-1.amazonaws.com -r /home/pi/aws_iot/aws-root-ca.pem -c /home/pi/aws_iot/yUp3qLUftKGGY01XdcL5/certificate.pem.crt -k /home/pi/aws_iot/yUp3qLUftKGGY01XdcL5/private.pem.key -n yUp3qLUftKGGY01XdcL5 -id yUp3qLUftKGGY01XdcL5 -ri 120 -as /home/pi/aws_iot/aws-rpi02-active-sensors.json 2>&1 | tee /home/pi/aws_iot/aws-thing-shadow3-$(date +%F-%H-%M).log
fi
