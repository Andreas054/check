from guizero import *

folderProgram = "/home/pi/check/"


nrCaractereProdusMAX = 20 # 4.2 + External
# nrCaractereProdusMAX = 9 # 3.5


dbdir = "192.168.10.100:D:/FBData/04/SMARTCASH.FDB"
# dbdir = "192.168.30.100:D:/IBData/SMARTCASH.FDB"
# dbdir = "192.168.40.100:D:/IBData/SMARTCASH.FDB"
# dbdir = "192.168.50.100:D:/IBData/SMARTCASH.FDB"
# dbdir = "192.168.100.100:D:/IBData/SMARTCASH.FDB"
# dbdir = "192.168.150.100:D:/FBData/04/SMARTCASH.FDB"
# dbdir = "192.168.0.100:D:/IBData/SMARTCASH.FDB"

#######################################################################
# Exteral Monitor
# app = App(width = 1000, height = 500, title = "checkPrice", bg = "white")
# text0 = Text(app, text = " ", size = 80, font = "Times New Roman", color = "blue")
# Picture = Picture(app, image = f"{folderProgram}logoExternal.png")
# text1 = Text(app, text = "Scanati produsul", size = 70, font = "Times New Roman", color = "blue")
# text2 = Text(app, text = "aici!", size = 70, font = "Times New Roman", color = "blue")
# text3 = Text(app, text = "...", size = 80, font = "Times New Roman", color = "red")
# text4 = Text(app, text = "", size = 40, font = "Times New Roman", color = "black")

# 3.5 LCD
# app = App(width = 1000, height = 500, title = "checkPrice", bg = "white")
# text0 = Text(app, text = " ", size = 10, font = "Times New Roman", color = "blue")
# Picture = Picture(app, image = f"{folderProgram}logo35.png")
# text1 = Text(app, text = "Scanati produsul", size = 35, font = "Times New Roman", color = "blue")
# text2 = Text(app, text = "aici!", size = 35, font = "Times New Roman", color = "blue")
# text3 = Text(app, text = "...", size = 55, font = "Times New Roman", color = "red")
# text4 = Text(app, text = "", size = 27, font = "Times New Roman", color = "black")

# 4.2 LCD
app = App(width = 1000, height = 500, title = "checkPrice", bg = "white")
text0 = Text(app, text = " ", size = 20, font = "Times New Roman", color = "blue")
Picture = Picture(app, image = f"{folderProgram}logo42.png")
text1 = Text(app, text = "Scanati produsul", size = 40, font = "Times New Roman", color = "blue")
text2 = Text(app, text = "aici!", size = 40, font = "Times New Roman", color = "blue")
text3 = Text(app, text = "...", size = 70, font = "Times New Roman", color = "red")
text4 = Text(app, text = "", size = 35, font = "Times New Roman", color = "black")
#######################################################################
