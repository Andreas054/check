# checkpi
This is made to run on the Raspberry Pi with a Desktop Environment.

Price checker python script.

# Additional modules
- libfbclient2 (apt)
- [guizero](https://pypi.org/project/guizero/)
- [fdb](https://pypi.org/project/fdb/)

- ## 3.5 GPIO LCD
- [LCD-show github](https://github.com/waveshare/LCD-show)
- [Waveshare 3.5" LCD](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A))

- ## 4.3 DSI LCD
- [Waveshare 4.3" LCD](https://www.waveshare.com/wiki/4.3inch_DSI_LCD)
```sh
sudo nano /boot/config.txt

dtoverlay=vc4-kms-v3d
dtoverlay=vc4-kms-dsi-7inch
```
#### Set permissions for changing screen brightness
```sh
sudo su -c 'echo SUBSYSTEM==\"backlight\", RUN+=\"/bin/chmod 0666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power\" > /etc/udev/rules.d/99-backlight.rules'
```


# Crontab
### root
```sh
0 0 * * 1 /sbin/shutdown -r
*/10 7-20 * * * python3 /home/pi/checkpi/watchdog_check.py
```

### rpi3fetcheck1
```sh
@reboot sh /home/pi/checkpi/startup.sh
5 6 * * * sh /home/pi/checkpi/startup.sh
55 21 * * * sh /home/pi/checkpi/stop.sh
0 22 * * * vcgencmd display_power 0
0 6 * * * vcgencmd display_power 1
```

### rpi4fetcheck2
```sh
@reboot sh /home/pi/checkpi/startup.sh
5 6 * * * sh /home/pi/checkpi/startup.sh
55 21 * * * sh /home/pi/checkpi/stop.sh
```
