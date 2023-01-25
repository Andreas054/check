import subprocess
import re
import os
import socket
import time
import datetime

#time.sleep(30)

# Server IP and port
UDP_IP_ADDRESS_SERVER = "192.168.150.100"
UDP_PORT_NO_SERVER = 9000

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSock.bind((UDP_IP_ADDRESS_SERVER, UDP_PORT_NO_SERVER))

dbdir = '"D:\IBData\SMARTCASH.FDB"'
#logfile = "C:\\Users\\VM\\Desktop\\checkLog.txt"
errmessage = ["Cod inexistent sau", "articol invalid"]

# Write to log current date
now = datetime.datetime.now()
tmp = os.system('echo ==================================== >> checkLog.txt')
tmp = os.system('echo Start program on : {}.{}.{} >> checkLog.txt'.format(now.day, now.month, now.year))

def isqlquery(selection, table, column, data):
    tmp=os.system('echo CONNECT {}; > inputfile'.format(dbdir))
    tmp=os.system('echo select {} from {} where {}={}; >> inputfile'.format(selection, table, column, data))
    return str(subprocess.check_output("isql.exe -u SYSDBA -p masterke -i inputfile",shell=True))
    
while True:
    # addr is sending device (sg15/rpi)
    data, addr = serverSock.recvfrom(1024)
    data.hex()
    data=str(data)

    # Write to log current time and COD
    now = datetime.datetime.now()
    tmp = os.system('echo ==================================== >> checkLog.txt')
    tmp = os.system('echo [{}:{}:{}] Request from {}, data={} >> checkLog.txt'.format(now.hour, now.minute, now.second, addr, data))

    # F products need last char removed, A products don't ???
    removecharbeg = 3
    if data[2] == "A":
        removechar = 3
    else:
        # EAN 8 has FF instead of F
        if data[3] == "F":
            removecharbeg = 4
        removechar = 4

    # Remove b' and '\r from beggining/end and add ' to each end
    data = data[removecharbeg:-removechar]
    data = "'" + data + "'"

    # Create inputfile for ARTNR
    isqloutput = isqlquery("ARTNR", "CODURI", "COD",  data)

    # Try in case of non existent COD
    try:
        # Find first number in string
        # Keep the string starting with first number
        # Position of first whitespace
        # Leave only PRET in variable
        artnr = re.search(r"\d", isqloutput)
        artnr = isqloutput[artnr.start():]
        removerest = re.search(r"\s", artnr)
        artnr = artnr[:removerest.start()]

    
    # On exception send error message and go back to the beggining of the loop
    except Exception as e:
        print("errmessage")
        tosend = "\x1b%\x1bB0\x1b$" + errmessage[0] + "\r\x1bB0\x1b.8" + errmessage[1]  + "\x03"
        serverSock.sendto(tosend.encode(), addr)
        # Write to log current time and error
        now = datetime.datetime.now()
        tmp = os.system('echo [{}:{}:{} ERR] {} >> checkLog.txt'.format(now.hour, now.minute, now.second, e))
        tmp = os.system('echo /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ >> checkLog.txt')
        continue

    # Create inputfile for PRET and IDTVA
    isqloutput = isqlquery("PRET,IDTVA", "CATALOG", "ARTNR", artnr)
    
    # Find first number (PRET) in string
    # Keep the string starting with first number
    # Position of first whitespace (after PRET)
    pret = re.search(r"\d", isqloutput)
    pret = isqloutput[pret.start():]
    removerestpret = re.search(r"\s", pret)

    # Keep string after PRET
    # Find first number (IDTVA) in PRET string
    # Keep the string starting with first number
    # Position of first whitespace (after IDTVA)
    # Leave only IDTVA in variable
    tva = pret[removerestpret.start():]
    removeresttva = re.search(r"\d", tva)
    tva = tva[removeresttva.start():]
    removeresttva = re.search(r"\s", tva)
    tva = tva[:removeresttva.start()]

    # Leave only PRET in variable
    pret = pret[:removerestpret.start()]

    # Convert IDTVA into actual TVA
    tva=float(tva)
    if tva==1:
        tva=1.19
    if tva==2:
        tva=1.09
    if tva==3:
        tva=1.05

    pretfinal = float(pret) * tva
    pretfinal = round(pretfinal, 2)
    
    # Create inputfile for DESCRIERE
    isqloutput = isqlquery("DESCRIERE", "CATALOG", "ARTNR", artnr)

    # Find first "== " and keep that in isqloutput string
    descriere = re.search("== ", isqloutput)
    isqloutput = isqloutput[descriere.start():]

    # Find first linebreak and keep that +2 characters in descriere string
    descriere = re.search(r"\\n", isqloutput)
    descriere = isqloutput[descriere.start()+2:]

    # Find 3 whitespaces in a row (indicating end of DESCRIERE) and keep that in descriere string
    removerestdescriere = re.search("   ", descriere)
    descriere = descriere[:removerestdescriere.start()]
    
    # Calculate half of descriere length and separate into 2 senteces keeping words intact
    descrierelen = int(len(descriere) / 2 - 1)
    descrierepos = re.search(r"\s", descriere[descrierelen:])
   
    # In case DESCRIERE isn't long enough or doesn't have a space
    try:
        descriere1 = descriere[:int(descrierepos.end()) + descrierelen]
        descriere2 = descriere[int(descrierepos.end()) + descrierelen:]
    except:
        descriere1 = descriere
        descriere2 = ""

    # Write to log current time, DESCRIERE and PRET
    now = datetime.datetime.now()
    tmp = os.system('echo [{}:{}:{}] {} , {} >> checkLog.txt'.format(now.hour, now.minute, now.second, descriere, str(pretfinal)))

    # Assemble message like SG15 and send back response
    tosend = "\x1b%\x1bB0\x1b$" + descriere1 + "\r" + descriere2 + "\r\x1bB1\x1b.8" + str(pretfinal) + " Lei/Buc\x03"
    print (tosend)
    print(addr)
    serverSock.sendto(tosend.encode(), addr)
    
