#!/bin/bash

sleep 15
export DISPLAY=:0
xhost +

sudo /usr/bin/lxterminal -e "/usr/bin/python3 /home/pi/checkpi/checkpi.py"
