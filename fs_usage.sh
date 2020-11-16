#!/bin/bash
fs_usage=`df -h / | tail -1 | awk '{print $5}'| sed 's/\%//'`
echo "{\"fs_usage\":$fs_usage}" > /home/pi/aws_iot/fs_usage.json
cat fs_usage.json