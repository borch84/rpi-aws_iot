#!/usr/bin/env python3

import subprocess



proc = subprocess.Popen(["wpa_cli", "-i", "wlan0", "reconfigure"],stdout=subprocess.PIPE)
(out, err) = proc.communicate()
#print(out)

if out in b'OK\n': #out es un objeto byte
	print('wpa_cli -i wlan0 reconfigure: OK!')
else: 
	print('wpa_cli -i wlan0 reconfigure: FAIL!')



