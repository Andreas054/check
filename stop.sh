#!/bin/bash

export DISPLAY=:0
xhost +

sudo killall lxterminal

echo 0 > /sys/class/backlight/10-0045/brightness  # for 4.2 inch display
