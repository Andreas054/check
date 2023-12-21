# Version 1.0

import sys
import os
import socket
import time
import datetime
from guizero import *
from threading import Thread

# IP addresses of client and server + UDP port of server
ip_addr_rpi = "192.168.100.133"
ip_addr_srv = "192.168.100.100"
port_client = 9000  # rpi sending port
port_server = 9001  # rpi listening port
delayvar = 6

# usbScan
# Client socket for Denumire, Pret produs
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSock.bind((ip_addr_rpi, 9001))

# usbListen
# Server(Listening) socket for COD
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSock.bind((ip_addr_rpi, port_server))

# Exteral Monitor
'''
app = App(width=1000, height=500, title="checkPrice", bg="white")
text0 = Text(app, text=" ", size=80, font="Times New Roman", color="blue")
Picture = Picture(app, image="/home/pi/checkpi/logo.png")
text1 = Text(app, text="Scanati Produsul!", size=60, font="Times New Roman", color="blue")
text1 = Text(app, text="aici", size=46, font="Times New Roman", color="blue")
text2 = Text(app, text="...", size=60, font="Times New Roman", color="red")
'''

# 3.5 LCD
app = App(width=1000, height=500, title="checkPrice", bg="white")
text0 = Text(app, text=" ", size=10, font="Times New Roman", color="blue")
Picture = Picture(app, image="/home/pi/checkpi/logo.png")
text1 = Text(app, text="Scanati Produsul!", size=35, font="Times New Roman", color="blue")
text2 = Text(app, text="aici", size=35, font="Times New Roman", color="blue")
text3 = Text(app, text="...", size=55, font="Times New Roman", color="red")

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
            if c > 0:
                ##  40 is carriage return which signifies
                ##  we are done looking for characters
                if int(c) == 40:
                    done = True
                    break;
                ##  If we are shifted then we have to
                ##  use the hid2 characters.
                if shift:
                    ## If it is a '2' then it is the shift key
                    if int(c) == 2:
                        shift = True
                    ## if not a 2 then lookup the mapping
                    else:
                        ss += hid2[int(c)]
                        shift = False
                ##  If we are not shifted then use
                ##  the hid characters
                else:
                    ## If it is a '2' then it is the shift key
                    if int(c) == 2:
                        shift = True
                    ## if not a 2 then lookup the mapping
                    else:
                        ss += hid[int(c)]
    return ss

def usbScan():
    global messageReceivedBool
    while True:
        output=barcode_reader()
        #output = "5942325000133"
        output = "Z" + output
        
        messageReceivedBool = False

        print(output)
        clientSock.sendto(output.encode(), (ip_addr_srv, port_client))
        time.sleep(delayvar)
        
        if messageReceivedBool == False:
            # Write to log current time and COD in case No Response
            now = datetime.datetime.now()
            tmp = os.system('echo "====================================" >> /home/pi/checkpi/checkLog.txt')
            tmp = os.system('echo "[{}:{}:{}] Request sent, cod={}" >> /home/pi/checkpi/checkLog.txt'.format(now.hour, now.minute, now.second, output))

def receiveAndDisplay():
    global messageReceivedBool
    while True:
        data, addr = serverSock.recvfrom(1024)
        data.hex()
        data = str(data)
        
        messageReceivedBool = True
        
        # example of data
        # b'\x1b%\x1bB0\x1b$BAUTURA WET HARD S\rELTZER 0.33L\r\x1bB1\x1b.85.69Lei/Buc\x03'
        # Remove everything until first "$" and delete the "\x03'"
        data = data[data.find('$') + 1:-5]

        # Find first and last "\r"
        mid1 = data.find('\\r')
        mid2 = data.rfind('\\r')

        # Find the price
        fin = data.find('1b.8') + 4

        # Save into variables the iterators where the first and last "\r" are
        tmp = len(data) - mid1
        tmp2 = len(data) - mid2

        # Remove the "\r" from between the name of the product
        line1 = data[:-tmp] + " " + data[mid1 + 2:-tmp2]

        # Write to log current time, name of product and price
        #now = datetime.datetime.now()
        #tmp = os.system('echo "[{}:{}:{}] {} ; {}" >> /home/pi/checkpi/checkLog.txt'.format(now.hour, now.minute, now.second, line1, data[fin:]))

        # Terminal window logging
        print(now.hour, now.minute, now.second)
        print(line1)
        print(data[fin:])

        # Display text on screen with name of product and price, wait 6 seconds and change back to default
        text1.value = line1
        text2.value = data[fin:]
        time.sleep(6)
        # External Monitor
        '''
        text1.value = "aici"
        text2.value = "..."
        '''

        # 3.5 LCD
        text1.value = "Scanati Produsul!"
        text2.value = "aici"
        text3.value = "..."

# Write to log current date
now = datetime.datetime.now()
tmp = os.system('echo ==================================== >> /home/pi/checkpi/checkLog.txt')
tmp = os.system('echo Start program on : {}.{}.{} >> /home/pi/checkpi/checkLog.txt'.format(now.day, now.month, now.year))

thread = Thread(target = receiveAndDisplay)
thread.start()
threadusbScan = Thread(target = usbScan)
threadusbScan.start()

app.set_full_screen()
app.display()

