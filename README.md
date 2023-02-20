# checkpi
This is made to run on the Raspberry Pi 32 bit version with a Desktop Environment.

Price checker python script communicating with the server running SmartCash Check through UDP.

## Additional libraries
- [guizero](https://pypi.org/project/guizero/)

## Crontab
### normal
- @reboot sh /home/pi/checkpi/startup.sh
- 5 6 * * * sh /home/pi/checkpi/startup.sh
- 55 21 * * * sh /home/pi/checkpi/stop.sh

\# For External Monitor
- 0 22 * * * vcgencmd display_power 0
- 0 6 * * * vcgencmd display_power 1
