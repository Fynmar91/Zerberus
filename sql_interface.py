#!/usr/bin/env python
#	Yannik Seitz 20.03.19
#	FS2V Tuerzugangs-Projekt
#	Diese Datei beinhaltet alle selbst geschriebenen SQL-Funktionen

import MySQLdb

	# Stellt SQL-Zugang zur Datenbank her
def SQLaccess(SQL):
	db = MySQLdb.connect(host=SQL[0], user=SQL[1], passwd=SQL[2], db=SQL[3])
	curser = db.cursor()
	return curser, db

	# Sucht Nutzerdaten in SQL-Datenbank, gibt Tupel zurueck
def readUser(tagID, SQL):
	curser, db = SQLaccess(SQL)
	curser.execute("SELECT * FROM Users WHERE tagID = %s", (tagID,))
	User = curser.fetchone()
	db.commit()
	if(User):
		return User
	else:
		return false

	# Sucht Raumdaten in SQL-Datenbank, gibt Tupel zurueck
def readRoom(SQL, room_number):
	curser, db = SQLaccess(SQL)
	curser.execute("SELECT * FROM Rooms WHERE roomNr = %s", (room_number,))
	Room = curser.fetchone()
	db.commit()
	if(Room):
		return Room
	else:
		return false

	# Logt im Fall: erfolgreicher Zugang
def writeLog1(event, tagID, SQL, room_number, User):
	curser, db = SQLaccess(SQL)
	curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, tagID, roomNr, User[1]))
	db.commit()

	# Logt im Fall: verweigerter Zugang
def writeLog0(event, tagID, SQL, room_number, User):
	curser, db = SQLaccess(SQL)
	curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, tagID, roomNr, User[1]))
	db.commit()

	# Logt im Fall: unbekannte RFID
def writeLog2(event, tagID, SQL, room_number):
	curser, db = SQLaccess(SQL)
	curser.execute("INSERT INTO Logs (event, tagID, roomNr, date, time) VALUES (%s, %s, %s, CURDATE(), CURRENT_TIME())", (event, tagID, roomNr))
	db.commit()

	# Setzt openFlag des Raums auf 0
def resetOpenFlag(SQL, room_number):
	curser, db = SQLaccess(SQL)
	curser.execute("UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s", (roomNr,))
	db.commit()

