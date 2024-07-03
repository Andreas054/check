#!/bin/bash

sleep 15
export DISPLAY=:0
xhost +

echo 255 > /sys/class/backlight/10-0045/brightness # for 4.2 inch display

sudo /usr/bin/lxterminal -e "/usr/bin/python3 /home/pi/check/checkpi.py"
