#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	SQL Interface v1.1
#	Yannik Seitz 11.04.19
#	Diese Datei beinhaltet alle Funktionen um mit dem SQL-Server zu komunizieren

import MySQLdb

	# Stellt SQL-Zugang zur Datenbank her
def SQLaccess(SQL):
	db = MySQLdb.connect(host=SQL[0], user=SQL[1], passwd=SQL[2], db=SQL[3])	# SQL = (sql_ip, sql_user, sql_password, sql_database)
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
		return False

	# Sucht Raumdaten in SQL-Datenbank, gibt Tupel zurueck
def readRoom(SQL, room_number):
	curser, db = SQLaccess(SQL)
	curser.execute("SELECT * FROM Rooms WHERE roomNr = %s", (room_number,))
	Room = curser.fetchone()
	db.commit()
	if(Room):
		return Room
	else:
		return False

	# Logt im Fall: erfolgreicher Zugang
def writeLog1(event, tagID, SQL, room_number, User):
	curser, db = SQLaccess(SQL)
	curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, tagID, room_number, User[1]))
	db.commit()

	# Logt im Fall: verweigerter Zugang
def writeLog0(event, tagID, SQL, room_number, User):
	curser, db = SQLaccess(SQL)
	curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, tagID, room_number, User[1]))
	db.commit()

	# Logt im Fall: unbekannte RFID
def writeLog2(event, tagID, SQL, room_number):
	curser, db = SQLaccess(SQL)
	curser.execute("INSERT INTO Logs (event, tagID, roomNr, date, time) VALUES (%s, %s, %s, CURDATE(), CURRENT_TIME())", (event, tagID, room_number))
	db.commit()

	# Setzt openFlag des Raums auf 0
def resetOpenFlag(SQL, room_number):
	curser, db = SQLaccess(SQL)
	curser.execute("UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s", (room_number,))
	db.commit()

