#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Zerberus v1.3
#	Yannik Seitz 30.04.19
#	Dieses Programm verarbeitet eingelesene RFID-tagIDs und ueberprueft ob sie zugangsberechtigt sind
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und ein Neustart durchgefuehrt

import time
import subprocess
import smtplib
import ssl
import RPi.GPIO as GPIO
import MySQLdb
import SimpleMFRC522
import ConfigParser

def main():
	door = Door()
	reader = SimpleMFRC522.SimpleMFRC522()
	while True:
		key = False
		GPIO.output(22,GPIO.HIGH) # Status LED Gruen
		key = reader.read_id() # RFID-Karte einlesen
		if(key):
			door.Open(key)
		else:
			print('ok')

def manual():
	door = Door()
	while True:
		door.ManualOpen()
		time.sleep(5)

class Door:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.number = config.get('ROOM', 'Raumnummer')
		self.sql = SQL()
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM) # GPIO in BCM mode
		GPIO.setup(17,GPIO.OUT) # Rot
		GPIO.setup(18,GPIO.OUT) # Tueroeffner
		GPIO.setup(22,GPIO.OUT) # Gruen
		GPIO.output(18,GPIO.HIGH) # Relais schliesst bei low

	def Open(self, key):
		event = self.sql.CheckPermission(key, self.number) # Zungangsberechtigung kontrollieren
		if(event == 1):
			self.Granted() # Event 1; Zugang erlaubt; Tuer oeffnen
		elif(event == 0):
			self.Denied() # Event 0; Kein Zugang; rote LED blinkt
		elif(event == 2):
			self.Unknown() # Event 2; Unbekannt; rote LED

	def ManualOpen(self): # Prueft ob openFlag gesetzt wurde
		if(self.sql.CheckManualAccess(self.number)):
			self.Granted() # Tuer oeffnen


	def Granted(self): # Tuer oeffnen
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

	def Denied(self): # Kein Zugang; rote LED blinkt
		for i in range(10):
			GPIO.output(17,GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(17,GPIO.LOW)
			time.sleep(0.05)

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
		event = 2
		if(User and Room):
			if(User[6] >= Room[6]):	# User[6] = Prio; Room[6] = Prio
				event = 1 # Event 1; Zugang erlaubt
			else:
				event = 0 # Event 0; Zugang verweigert
		elif(User == False and Room):
			event = 2 # Event 2; Unbekannt
		self.Log(event, key, number, User[1]) # Event protokollieren
		return event

	def Log(self, event, key, number, name):	# Event protokollieren
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, key, number, name))
		db.commit()
		db.close()

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

	def DelLogs(self): # SQL Anfrage
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("DELETE FROM Logs")
		db.commit()
		db.close()

	def CheckManualAccess(self, number):	# Prueft ob openFlag gesetzt wurde
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", number)
		if(Room):
			if(Room[7] == 1):	# Room[7] = Rooms; openFlag
				self.ResetOpenFlag(number)
				return True

	def ResetOpenFlag(self, number):	# Setzt openFlag des Raums auf 0
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s", (number,))
		db.commit()
		db.close()

class Mail:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.address = config.get('EMAIL', 'Adresse')
		self.password = config.get('EMAIL', 'Passwort')
		self.port = config.getint('EMAIL', 'Port')
		self.smtp = config.get('EMAIL', 'smtpAdresse')

	def SendArchive(self, logs, subject): # Email senden
		list = ''
		for tuple in logs:
			list = '{}\n\n{}'.format(list, tuple)
		message = 'Subject: {}\n\n{}'.format(subject, list)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)

	def SendError(self, error, subject): # Email senden
		error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
		message = 'Subject: {}\n\n{}'.format(subject, error)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = Mail()
		mail.SendError(error, 'ZERBERUS ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
else:
	try:
		manual()

	except Exception as error:
		mail = Mail()
		mail.SendError(error, 'PUPPY ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
