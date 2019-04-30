#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Door Class v1.0
#	Yannik Seitz 30.04.19

import ConfigParser
import MySQLdb

class Door:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.ip = config.get('SQL', 'IP')
		self.user = config.get('SQL', 'Nutzer')
		self.password = config.get('SQL', 'Passwort')
		self.database = config.get('SQL', 'DatenbankName')
		self.number = config.get('ROOM', 'Raumnummer')

	def Check(self, key):	# Zungangsberechtigung kontrollieren
		User = self.Query("SELECT * FROM Users WHERE tagID = %s", key)
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", self.number)
		if(User and Room):
			if(User[6] >= Room[6]):	# User[6] = Prio; Room[6] = Prio
				return 1, User[1]	# Event 1; Zugang erlaubt
			else:
				return 0, User[1]	# Event 0; Zugang verweigert
		elif(User == False and Room):
			return 2, 'Unbekannt'	# Event 2; Unbekannt

	def CheckManualOpen(self):	# Prueft ob openFlag gesetzt wurde
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", self.number)
		if(Room):
			if(Room[7] == 1):	# Room[7] = Rooms; openFlag
				self.Open()
				self.ResetOpenFlag()

	def Query(self, query, var): # SQL Anfrage
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute(query, (var,))
		result = curser.fetchone()
		db.commit()
		db.close()
		if(result):
			return result
		else:
			return False

	def Log(self, event, key, name):	# Event protokollieren
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, key, self.number, name))
		db.commit()
		db.close()

	def ResetOpenFlag(self):	# Setzt openFlag des Raums auf 0
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s", (self.number,))
		db.commit()
		db.close()

	def Open(self):	# Tuer oeffnen
		GPIO.output(18,GPIO.LOW)
		for i in range(10):
			GPIO.output(22,GPIO.HIGH)
			time.sleep(0.2)
			GPIO.output(22,GPIO.LOW)
			time.sleep(0.1)
		GPIO.output(18,GPIO.HIGH)

	def Unknown(self): # Unbekannt; rote LED
		GPIO.output(17,GPIO.HIGH)
		time.sleep(1)
		GPIO.output(17,GPIO.LOW)

	def Prohibited(self):	# Kein Zugang; rote LED blinkt
		for i in range(10):
			GPIO.output(17,GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(17,GPIO.LOW)
			time.sleep(0.05)
