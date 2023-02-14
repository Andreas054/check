#!/usr/bin/python
import sys
import os
import socket
import time
import datetime

# IP addresses of client and server + UDP port of server
ip_addr_rpi = "192.168.100.133"
ip_addr_srv = "192.168.100.100"
port = 9000
delayvar = 6

def barcode_reader():
    """Barcode code obtained from 'brechmos' 
    https://www.raspberrypi.org/forums/viewtopic.php?f=45&t=55100"""
    hid = {4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm',
           17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y',
           29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ',
           45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';', 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'}
    hid2 = {4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M',
            17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y',
            29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 44: ' ',
            45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':', 52: '"', 53: '~', 54: '<', 55: '>', 56: '?'}

    fp = open('/dev/hidraw0', 'rb')
    ss = ""
    shift = False
    done = False
    while not done:
        ## Get the character from the HID
        buffer = fp.read(8)
        for c in buffer:
            if ord(c) > 0:
                ##  40 is carriage return which signifies
                ##  we are done looking for characters
                if int(ord(c)) == 40:
                    done = True
                    break;
                ##  If we are shifted then we have to
                ##  use the hid2 characters.
                if shift:
                    ## If it is a '2' then it is the shift key
                    if int(ord(c)) == 2:
                        shift = True
                    ## if not a 2 then lookup the mapping
                    else:
                        ss += hid2[int(ord(c))]
                        shift = False
                ##  If we are not shifted then use
                ##  the hid characters
                else:
                    ## If it is a '2' then it is the shift key
                    if int(ord(c)) == 2:
                        shift = True
                    ## if not a 2 then lookup the mapping
                    else:
                        ss += hid[int(ord(c))]
    return ss

# Establish connection with the server
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSock.bind((ip_addr_rpi, 9001))

# Write to log current date
now = datetime.datetime.now()
tmp = os.system('echo ==================================== >> /home/pi/checkpi/checkLog.txt')
tmp = os.system('echo Start program on : {}.{}.{} >> /home/pi/checkpi/checkLog.txt'.format(now.day, now.month, now.year))

os.system("python3 /home/pi/checkpi/usbListen.py &")

while True:
    output=barcode_reader()
    output="Z"+output

    # Write to log current time and COD
    now = datetime.datetime.now()
    tmp = os.system('echo "====================================" >> /home/pi/checkpi/checkLog.txt')
    tmp = os.system('echo "[{}:{}:{}] Request sent, cod={}" >> /home/pi/checkpi/checkLog.txt'.format(now.hour, now.minute, now.second, output))

    print(output)
    clientSock.sendto(output, (ip_addr_srv, port))
    time.sleep(delayvar)
