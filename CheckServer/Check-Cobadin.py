import subprocess
import re
import os
import socket
import time
import datetime

time.sleep(30)

# PROGRAM CONFIG ##########################################################
# Server IP and port
UDP_IP_ADDRESS_SERVER = "192.168.150.100"
UDP_PORT_NO_SERVER = 9000

# Windows = 0 || Linux = 1
boolOS = 0

pythondirwindows = "C:/Users/Operator/AppData/Local/Programs/Python/Python37/"

ipserver = ""	# LEAVE EMPTY IF RUNNING ON SAME MACHINE AS DATABASE; example "192.168.100.100:"
dbdir = '"{}D:/IBData/SMARTCASH.FDB"'.format(ipserver)
errmessage = ["Cod inexistent sau", "articol invalid"]

###########################################################################

# Set parameters based on what OS is running
if boolOS == 0:
    isqlexecutable = "isql.lnk"
    quotation = ''
else:
    pythondirwindows = ""
    isqlexecutable = "./isql"
    quotation = '"'

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSock.bind((UDP_IP_ADDRESS_SERVER, UDP_PORT_NO_SERVER))

# Write to log current date and mark start of program
now = datetime.datetime.now()
tmp = os.system('echo {}===================================={} >> checkLog.txt'.format(quotation, quotation))
tmp = os.system('echo {}Start program on : {}.{}.{}{} >> checkLog.txt'.format(quotation, now.day, now.month, now.year, quotation))

def isqlquery(selection, table, column, data):
    tmp=os.system('echo {}CONNECT {};{} > inputfile'.format(quotation, dbdir, quotation))
    tmp=os.system('echo {}SELECT {} FROM {} WHERE {}={};{} >> inputfile'.format(quotation, selection, table, column, data, quotation))
    return str(subprocess.check_output(isqlexecutable + " -u SYSDBA -p masterke -i {}inputfile".format(pythondirwindows),shell=True))

while True:
    # Get data from client
    # addr is sending device (sg15/rpi)
    # Example from Shuttle "F4605496001584\r" or in HEX "46343630353439363030313538340d"
    # Example from RaspberryPi "b'Z5942325000233'"
    data, addr = serverSock.recvfrom(1024)
    data.hex()
    # Transform the string removing unwanted characters => "Z5942325000233"
    data=str(data)[2:-1]

    # Write to log current time, IP Address + PORT of client and COD 
    now = datetime.datetime.now()
    tmp = os.system('echo {}===================================={} >> checkLog.txt'.format(quotation, quotation))
    tmp = os.system('echo {}[{}:{}:{}] Request from {}, data={}{} >> checkLog.txt'.format(quotation, now.hour, now.minute, now.second, addr, data, quotation))

    # Requests coming from RaspberryPis begin with 'Z' and don't need to be worked on
    # F products need last char removed, however A and FF (EAN-8) products don't ???; ALSO IF THE STRING LENGTH IS LESS THAN 8 = cod PLU so don't remove anything
    # Variable for removing A/F/Z
    removecharbeg = 1
    removechar = 0

    # THIS SHOULD BE TEMPORARY =================================================
    isrpi = 0
    if data[0] == "Z":
        isrpi = 1
    # ==========================================================================

    if data[len(data)-1] == "r":
        removechar = 2
    if data[0] == "A" or len(data) < 8:
        removechar = 0
    else:
        # If COD starts with 0 it doesn't need to be changed
        if data[1] == "0":
            removecharbeg = 1
            removechar = 0
        else:
            # EAN 8 has FF instead of F
            if data[1] == "F":
                removecharbeg = 2
            removechar = removechar + 1

    # Format the data string accordingly to remove the A/F/FF/Z from the beggining 
    if removechar == 0:
        data = data[removecharbeg:]
    else:
        data = data[removecharbeg:-removechar]

    # NEED TO ADD COMMENTS HERE!!!!!!!!!!!!!!!!!
    greutate =""
    um = "Buc"
    # If COD is from CANTAR it begins with 28 (probably)
    if data[0]=="2" and data[1]=="8":
        #data[len(data)-1]
        #greutate = data[-3:]
        if isrpi == 0:
            greutate = data[-5:-3]
            greutate = greutate + "." + data[-3:]
            greutate = "\r" + str(float(greutate)) + " kg"
        #convert data to 0000 final
        data = data[:-5] + "00000"
        print(data)
        um = "Kg"

    # Add ' to each end
    data = "'" + data + "'"

    print (data)
    
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

    # On exception send error message to the CLIENT
    except Exception as e:
        print("errmessage")
        # Shuttle need special formatting to display on different lines; REFER TO USER MANUAL FOR HEX CODES
        tosend = "\x1b%\x1bB0\x1b$" + errmessage[0] + "\r\x1bB0\x1b.8" + errmessage[1]  + "\x03"
        serverSock.sendto(tosend.encode(), addr)
        # Write to log current time and error
        now = datetime.datetime.now()
        tmp = os.system('echo {}[{}:{}:{} ERR] {}{} >> checkLog.txt'.format(quotation, now.hour, now.minute, now.second, e, quotation))
        tmp = os.system('echo {}/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\{} >> checkLog.txt'.format(quotation, quotation))
        # Go back to the beggining of the loop
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

    # Calculate the actual price using TVA and round it to 2 decimals
    pretfinal = float(pret) * tva
    pretfinal = round(pretfinal, 2)
    
    # Create inputfile for DESCRIERE (nume produs)
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
    tmp = os.system('echo {}[{}:{}:{}] {} , {}{} >> checkLog.txt'.format(quotation, now.hour, now.minute, now.second, descriere, str(pretfinal), quotation))

    # Assemble message like Check and send back response to the client
    tosend = "\x1b%\x1bB0\x1b$" + descriere1 + "\r" + descriere2 + greutate + "\r\x1bB1\x1b.8" + str(pretfinal) + " Lei/" + um + "\x03"
    #tosend = "\x1b%\x1bB0\x1b$" + descriere1 + "\r" + descriere2 + "\r\x1bB1\x1b.8" + str(pretfinal) + " Lei/Buc\x03"
    print (tosend)
    print (addr)
    serverSock.sendto(tosend.encode(), addr)
    
