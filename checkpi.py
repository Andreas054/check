# Version 1.1

import fdb
import time
import datetime
from threading import Thread

from config import *

countScannerUsage = 0

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
                    break
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

def checkTimeSaveLog():
    global countScannerUsage

    while True:
        now = datetime.datetime.now()
        currentTime = int(now.strftime("%H%M"))
        if 2150 - currentTime <= 30:
            with open(folderProgram + "checkLog.txt", "a") as logFile:
                logFile.write(f"[{datetime.datetime.now()}] : Nr citiri = {countScannerUsage}\n")
            import sys
            sys.exit() # exit Thread
        time.sleep(30 * 60)

def separaParagrafPeLinii(paragraf, maxWordLength):
    tmpRezultat = ""
    tmpRezultatLista = []
    contor = 0
    for cuvant in paragraf.split():
        tmpRezultat += cuvant + ' '
        contor += len(cuvant) + 1
        if contor > maxWordLength:
            contor = 0
            tmpRezultatLista.append(tmpRezultat)
            tmpRezultat = ""
    if len(tmpRezultatLista) > 0:
        paragraf = tmpRezultatLista
        if contor > 0:
            tmpRezultatLista.append(tmpRezultat)
    else:
        paragraf = [paragraf]

    return paragraf

def usbScan():
    global countScannerUsage
    while True:
        output = barcode_reader()
        #output = "5942325003753"

        fdbConnection = fdb.connect(dsn = dbdir, user = "sysdba", password = "masterkey") # Firebird
        fdbCursor1 = fdbConnection.cursor()

        fdbSQLCommand = f"SELECT cat.descriere, ROUND(cat.pret * (SELECT tva/100+1 FROM tva WHERE idtva = cat.idtva), 2), \
            (SELECT um FROM um WHERE idum = cat.idumsale), idtypeasociat, idarticol_asociat FROM catalog cat WHERE artnr = (SELECT artnr FROM coduri WHERE codwithcrc = '{output}');"

        fdbCursor1.execute(fdbSQLCommand)
        listaCursor1 = fdbCursor1.fetchall()

        countScannerUsage += 1

        if len(listaCursor1) == 0:
            print("cod inexistent")
            text1.value = "Articol inexistent"
            text2.value = "sau cod invalid"
            text3.value = output
            text4.value = ""

            # Write to log current time and COD in case No Response
            with open(folderProgram + "checkLog.txt", "a") as logFile:
                logFile.write(f"[{datetime.datetime.now()}] : Eroare cod = {output}\n")
        else:
            produsNume = listaCursor1[0][0]
            produsPret = listaCursor1[0][1]
            produsUM = listaCursor1[0][2]
            produsIdTypeAsociat = listaCursor1[0][3]
            produsIdArticolAsociat = listaCursor1[0][4]

            garantieNume = None
            garantiePret = None

            if produsIdTypeAsociat == 4: # Articol Principal RetuRO
                if produsIdArticolAsociat != 0:
                    fdbSQLCommand = f"SELECT descriere, pret FROM catalog WHERE artnr = {produsIdArticolAsociat};"

                    fdbCursor1.execute(fdbSQLCommand)
                    listaCursor2 = fdbCursor1.fetchall()

                    if len(listaCursor2) > 0:
                        garantieNume = listaCursor2[0][0]
                        garantiePret = listaCursor2[0][1]

            # CHANGE PARAMTER FOR DIFFERENT SIZE MONITOR
            produsNume = separaParagrafPeLinii(produsNume, nrCaractereProdusMAX) + ['']

            print(produsNume)
            print(produsPret, produsUM)

            # Display text on screen with name of product and price, wait 6 seconds and change back to default
            text1.value = produsNume[0]
            text2.value = produsNume[1]
            text3.value = str(produsPret) + '/' + produsUM
            if garantieNume is not None:
                text4.value = f'+ {garantiePret} {garantieNume}'

        time.sleep(6)

        text1.value = "Scanati produsul"
        text2.value = "aici!"
        text3.value = "..."
        text4.value = ""

# Write to log current date
with open(folderProgram + "checkLog.txt", "a") as logFile:
    logFile.write(f"[{datetime.datetime.now()}] : Started program\n")

threadusbScan = Thread(target = usbScan)
threadusbScan.start()

threadcheckTimeSaveLog = Thread(target = checkTimeSaveLog)
threadcheckTimeSaveLog.start()

app.set_full_screen()
app.display()
