#!/bin/bash

sleep 15
export DISPLAY=:0
xhost +

sudo /usr/bin/lxterminal -e "/usr/bin/python /home/pi/checkpi/usbScan.py"
