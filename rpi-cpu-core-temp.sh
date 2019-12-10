#!/bin/sh

 echo "{\"CPUTemp\":$(/usr/bin/vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')}"
