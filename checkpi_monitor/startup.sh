#!/bin/bash

sleep 15
export DISPLAY=:0
xhost +

sudo /usr/bin/lxterminal -e "/usr/bin/python2 /home/pi/checkpi/usbScan.py"
