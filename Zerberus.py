#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Zerberus v1.4
#	Yannik Seitz 01.05.19
#	Wird dieses Programm direkt ausgefuehrt erstellt es ein Objekt fuer einen RFID-Reader und eine Tuer-Kontrolle. Danach wird eine Endlosschleife gestartet.
#	In der Schleife wird abwechselnd versucht ein RFID-Schluessel zu finden oder kontrolliert ob die Tuer uber das Web-Interface geoeffnet werden soll.
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und ein Neustart durchgefuehrt

import time
import subprocess
import smtplib
import ssl
import RPi.GPIO as GPIO
import MySQLdb
import SimpleMFRC522
import ConfigParser


# ================================================================================
#				Main
# Objekte werden erstellt; Endlosschleife 
# ================================================================================
def main():
	i = 0
	door = DoorControl()
	reader = SimpleMFRC522.SimpleMFRC522()
	while True:
		key = False
		# Status LED Gruen
		GPIO.output(22,GPIO.HIGH)
		# RFID-Karte einlesen
		key = reader.read_id()
		if(key):
			# Versuche Tuer zu oeffnen
			door.Open(key)
		elif(i < 5):
			i = i + 1
			print(i)
		else:
			door.ManualOpen()
			i = 0
			print('go')


# ================================================================================
#				Klasse: DoorControl
# Kontrolliert das Relais und die LEDs
# Erstellt eine SQL-Objekt

# Open() ueberprueft ob der mitgegeben Schluessel zugangsberechtigt ist
# Input: RFID-ID | Output:

# ManualOpen() oeffnet die Tuer sollte eine Aufforderung in der Datenbank vorhanden sein
# Input:  | Output:

# Granted() schaltet das Relais ueber GPIO um die Tuer zu oeffnen
# Input:  | Output:

# Unknown() laesst die rote LED kurz leuchten
# Input:  | Output:

# Denied() laesst die rote LED blinken
# Input:  | Output:
# ================================================================================
class DoorControl:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('/home/pi/Zerberus/config.ini')
		self.number = config.get('ROOM', 'Raumnummer')
		self.sql = SQL()

		# GPIO in BCM mode
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM) 
		# Rot
		GPIO.setup(17,GPIO.OUT) 
		# Tueroeffner
		GPIO.setup(18,GPIO.OUT) 
		# Gruen
		GPIO.setup(22,GPIO.OUT) 
		# Relais schliesst bei low
		GPIO.output(18,GPIO.HIGH) 

	def Open(self, key):
		# Zungangsberechtigung kontrollieren
		event = self.sql.CheckPermission(key, self.number) 
		if(event == 1):
			# Event 1 = Zugang erlaubt; Tuer oeffnen
			self.Granted() 
		elif(event == 0):
			# Event 0 = Kein Zugang; rote LED blinkt
			self.Denied() 
		elif(event == 2):
			# Event 2 = Unbekannt; rote LED
			self.Unknown() 

	# Prueft ob openFlag gesetzt wurde
	def ManualOpen(self):
		if(self.sql.CheckManualAccess(self.number)):
			# Tuer oeffnen
			self.Granted()

	# Tuer oeffnen
	def Granted(self):
		GPIO.output(18,GPIO.LOW)
		for i in range(10):
			GPIO.output(22,GPIO.HIGH)
			time.sleep(0.2)
			GPIO.output(22,GPIO.LOW)
			time.sleep(0.1)
		GPIO.output(18,GPIO.HIGH)

	# Unbekannt; rote LED
	def Unknown(self):
		GPIO.output(17,GPIO.HIGH)
		time.sleep(1)
		GPIO.output(17,GPIO.LOW)

	# Kein Zugang; rote LED blinkt
	def Denied(self):
		for i in range(10):
			GPIO.output(17,GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(17,GPIO.LOW)
			time.sleep(0.05)


# ================================================================================
#				Klasse: SQL

# CheckPermission() prueft ob ein RFID-Schluessel zugriff zu einem Raum hat
# Input: RFID-ID ; Raumnummer | Output: Ereignis (Event 1 = Zugang erlaubt ; Event 0 = Zugang verweigert ; Event 2 = Unbekannt)

# Log() protokolliert ein Ereignis
# Input:  | Output:

# Query() stellt eine Abfrage an den SQL-Server
# Input:  | Output: Ergebnis der Abfrage

# DelLogs() loescht alle Logs
# Input:  | Output:

# CheckManualAccess() prueft ob ein Raum durch das Interface geoeffnet werden soll
# Input:  | Output: True/False
# ================================================================================
class SQL:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('/home/pi/Zerberus/config.ini')
		self.ip = config.get('SQL', 'IP')
		self.user = config.get('SQL', 'Nutzer')
		self.password = config.get('SQL', 'Passwort')
		self.database = config.get('SQL', 'DatenbankName')

	# Zungangsberechtigung kontrollieren
	def CheckPermission(self, key, number):
		User = self.Query("SELECT * FROM Users WHERE tagID = %s", key)
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", number)
		event = 2
		if(User and Room):
			# User[6] = Prio; Room[6] = Prio
			if(User[6] >= Room[6]):
				# Event 1 = Zugang erlaubt
				event = 1
			else:
				# Event 0 = Zugang verweigert
				event = 0
		elif(User == False and Room):
			# Event 2 = Unbekannt
			event = 2
		# Event protokollieren
		self.Log(event, key, number, User[1]) 
		return event

	# Event protokollieren
	def Log(self, event, key, number, name):
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, key, number, name))
		db.commit()
		db.close()

	# SQL Anfrage
	def Query(self, query, variable):
		result = False
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute(query, (variable,))
		result = curser.fetchone()
		db.commit()
		db.close()
		return result

	# Prueft ob openFlag gesetzt wurde
	def CheckManualAccess(self, number):
		Room = self.Query("SELECT * FROM Rooms WHERE roomNr = %s", number)
		if(Room):
			# Room[7] = Rooms; openFlag
			if(Room[7] == 1):
				self.ResetOpenFlag(number)
				return True

	# Setzt openFlag des Raums auf 0
	def ResetOpenFlag(self, number):
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s", (number,))
		db.commit()
		db.close()

	# SQL Anfrage
	def GetLogs(self):
		result = False
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("SELECT * FROM Logs")
		result = curser.fetchall()
		db.commit()
		db.close()
		return result

	# SQL Anfrage
	def DelLogs(self):
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("DELETE FROM Logs")
		db.commit()
		db.close()

# ================================================================================
#				Klasse: Mail

# SendError() protokolliert ein Ereignis
# Input: Error ;  Betreff | Output:
# ================================================================================
class Mail:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('/home/pi/Zerberus/config.ini')
		self.address = config.get('EMAIL', 'Adresse')
		self.password = config.get('EMAIL', 'Passwort')
		self.port = config.getint('EMAIL', 'Port')
		self.smtp = config.get('EMAIL', 'smtpAdresse')

	# Email senden
	def SendArchive(self, logs, subject):
		list = ''
		for tuple in logs:
			list = '{}\n\n{}'.format(list, tuple)
		message = 'Subject: {}\n\n{}'.format(subject, list)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)

	# Error per Email senden
	def SendError(self, error, subject):
		error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
		message = 'Subject: {}\n\n{}'.format(subject, error)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)


# ================================================================================
#				Ausfuehren als __main__
# ================================================================================
if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		print(error)
		mail = Mail()
		mail.SendError(error, 'ZERBERUS ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)

# ================================================================================
#				Ausfuehren als Archive
# ================================================================================
else:
	try:
		sql = SQL()
		mail = Mail()
		logs = sql.GetLogs()
		mail.SendArchive(logs, 'Logarchiv:')
		sql.DelLogs()

	except Exception as error:
		mail = Mail()
		mail.SendError(error, 'ARCHIVE ERROR:')