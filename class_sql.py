#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	SQL Klasse v1.0
#	Yannik Seitz 30.04.19

import time
import ConfigParser
import MySQLdb
import RPi.GPIO as GPIO

class SQL:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.ip = config.get('SQL', 'IP')
		self.user = config.get('SQL', 'Nutzer')
		self.password = config.get('SQL', 'Passwort')
		self.database = config.get('SQL', 'DatenbankName')

	def CheckPermission(self, key, number):	# Zungangsberechtigung kontrollieren
		User = self.Query("SELECT * FROM Users WHERE tagID = %s", key)
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", number)
		if(User and Room):
			if(User[6] >= Room[6]):	# User[6] = Prio; Room[6] = Prio
				return 1, User[1]	# Event 1; Zugang erlaubt
			else:
				return 0, User[1]	# Event 0; Zugang verweigert
		elif(User == False and Room):
			return 2, 'Unbekannt'	# Event 2; Unbekannt

	def CheckManualOpen(self, number):	# Prueft ob openFlag gesetzt wurde
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", number)
		if(Room):
			if(Room[7] == 1):	# Room[7] = Rooms; openFlag
				self.ResetOpenFlag(number)
				return True

	def Query(self, query, variable): # SQL Anfrage
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute(query, (variable,))
		result = curser.fetchone()
		db.commit()
		db.close()
		if(result):
			return result
		else:
			return False

	def GetLogs(self): # SQL Anfrage
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("SELECT * FROM Logs")
		result = curser.fetchall()
		db.commit()
		db.close()
		if(result):
			return result
		else:
			return False

	def Log(self, event, key, number, name):	# Event protokollieren
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, key, number, name))
		db.commit()
		db.close()

	def ResetOpenFlag(self, number):	# Setzt openFlag des Raums auf 0
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s", (number,))
		db.commit()
		db.close()
