#!/usr/bin/python
import socket
import os
import time
import datetime
import re
from guizero import *
from threading import Thread

app = App(width=1000, height=500, title="checkPrice", bg="white")
text0 = Text(app, text=" ", size=10, font="Times New Roman", color="blue")
Picture = Picture(app, image="/home/pi/checkpi/logo.png")
text1 = Text(app, text="Scanati Produsul!", size=35, font="Times New Roman", color="blue")
text2 = Text(app, text="aici", size=35, font="Times New Roman", color="blue")
text3 = Text(app, text="...", size=55, font="Times New Roman", color="red")

# IP address and UDP port of client
UDP_IP_ADDRESS = "192.168.100.133"
UDP_PORT_NO = 9001

# Establish connection with the server
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

def getVal():
    while True:
        data, addr = serverSock.recvfrom(1024)
        data.hex()
        data=str(data)
        # example of data
        # b'\x1b%\x1bB0\x1b$BAUTURA WET HARD S\rELTZER 0.33L\r\x1bB1\x1b.85.69Lei/Buc\x03'
        # Remove everything until first "$" and delete the "\x03'"
        data=data[data.find('$')+1:-5]

        # Find first and last "\r"
        mid1=data.find('\\r')
        mid2=data.rfind('\\r')

        # Find the price
        fin=data.find('1b.8')+4

        # Save into variables the iterators where the first and last "\r" are
        tmp=len(data)-mid1
        tmp2=len(data)-mid2

        # Remove the "\r" from between the name of the product
        line1=data[:-tmp] + " " + data[mid1+2:-tmp2]

        # Write to log current time, name of product and price
        now = datetime.datetime.now()
        tmp = os.system('echo "[{}:{}:{}] {} ; {}" >> /home/pi/checkpi/checkLog.txt'.format(now.hour, now.minute, now.second, line1, data[fin:]))

        # Terminal window logging
        print (now.hour , now.minute , now.second)
        print (line1)
        print (data[fin:])

        linelen = int(len(line1) / 2 -1)
        linepos = re.search(r"\s", line1[linelen:])
        try:
            line1a = line1[:int(linepos.end()) + linelen]
            line1b = line1[int(linepos.end()) + linelen:]
        except:
            line1a = line1
            line1b = line1
        # Display text on screen with name of product and price, wait 6 seconds and change back to default
        text1.value = line1a
        text2.value = line1b
        text3.value = data[fin:]
        time.sleep(6)
        text1.value = "Scanati Produsul!"
        text2.value = "aici"
        text3.value = "..."

thread = Thread(target = getVal)
thread.start()
app.set_full_screen()
app.display()
