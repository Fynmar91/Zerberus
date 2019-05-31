#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Zerberus v1.9
#	Yannik Seitz 25.05.19
#	Wird dieses Programm direkt ausgefuehrt erstellt es ein Tuer-Objekt und fuehrt dessen Start()-Funktion in einer Endlosschleife aus. 
#	Darin wird versucht ein RFID-Schluessel zu finden. 
#	Wird einer gefunden, stellt das System eine Anfrage an den SQL-Server um festzustellen ob der Zungang erlaubt ist.
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und nach 2 Minuten ein Neustart durchgefuehrt.

#	Die Funktionen Archive und Manual sind fuer externe Anwendungen

import time
import subprocess
import smtplib
import ssl
import socket
import fcntl
import struct
import RPi.GPIO as GPIO
import MySQLdb
import SimpleMFRC522
import ConfigParser
from rpi_ws281x import *

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

import xlwt
from tempfile import TemporaryFile

# ================================================================================
#				Main
# Objekte werden erstellt; Endlosschleife 
# ================================================================================
def main():
	door1 = DoorControl()

	while True:
		door1.Start()

# ================================================================================
#				Klasse: DoorControl
# Kontrolliert alle Funktionen einer Tuer
# Erstellt ein SQL-, LED- und SimpleMFRC522-Objekt

# Start() Hier startet das Programm. Es wird ueberprueft ob Datenbankzugang besteht.
# Input: | Output:

# Unlock() Versucht die Tuer zu oeffnen mit dem mitgegeben Schluessel zu oeffnen. 
# Input: RFID-ID | Output:

# ManualUnlock() Oeffnet die Tuer sollte eine Aufforderung in der Datenbank vorhanden sein
# Input: | Output:

# Open() Schaltet das Relais ueber GPIO um die Tuer zu oeffnen
# Input: | Output:

# Unknown() Laesst die rote LED kurz leuchten
# Input:  | Output:

# Denied() Laesst die rote LED blinken
# Input:  | Output:

# RoomMissing() Schaltet die oragene LED ein 
# Input:  | Output:
# ================================================================================
class DoorControl:
	def __init__(self):
		# GPIO in BCM mode
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM) 
		# Tueroeffner
		GPIO.setup(18,GPIO.OUT) 
		# Relais schliesst bei low
		GPIO.output(18,GPIO.HIGH) 
		config = ConfigParser.RawConfigParser()
		config.read('/home/pi/Zerberus/config.ini')
		self.roomNumber = config.get('ROOM', 'Raumnummer')
		self.error = True
		self.sql1 = SQL()
		self.sql1.SetIP(self.roomNumber)
		self.led1 = LED()
		self.reader1 = SimpleMFRC522.SimpleMFRC522()
		self.led1.StartUp()

	def Start(self):
		if (self.error == False):
			self.led1.Blau()
			key = False
			key = self.reader1.read_id_Cont()
			self.Unlock(key)
		else:
			while(self.error == True):
				self.Unlock(1337)
				time.sleep(4)

	def Unlock(self, key):
		self.error = False
		# Zungangsberechtigung kontrollieren
		event = self.sql1.CheckPermission(key, self.roomNumber) 
		if(event == 1):
			# Event 1 = Zugang erlaubt; Tuer oeffnen
			self.Open()
		elif(event == 0):
			# Event 0 = Kein Zugang; rote LED blinkt
			self.Denied()
		elif(event == 2):
			# Event 2 = Unbekannt; rote LED
			self.Unknown()
		elif(event == 3):
			# Event 3 = Raum Unbekannt
			self.RoomMissing()
			self.error = True

	# Prueft ob openFlag gesetzt wurde
	def ManualUnlock(self):
		if(self.sql1.CheckManualAccess(self.roomNumber)):
			# Tuer oeffnen
			self.Granted()
			self.led1.Blau()

	# Tuer oeffnen; gruene LED
	def Open(self):
		self.led1.Gruen()
		GPIO.output(18,GPIO.LOW)
		time.sleep(4)
		GPIO.output(18,GPIO.HIGH)

	# Unbekannt; rote LED
	def Unknown(self):
		self.led1.Rot()

	# Kein Zugang; rote LED blinkt
	def Denied(self):
		self.led1.RotBlink()

	# Raum nicht gefunden; orangene LED
	def RoomMissing(self):
		self.led1.Orange()

# ================================================================================
#				Klasse: SQL
# Fuehrt SQL-Abfragen durch, schreibt Ereignissprotokolle und setzt die openFalg zurueck

# CheckPermission() Prueft ob ein RFID-Schluessel zugriff zu einem Raum hat
# Input: RFID-ID ; Raumnummer | Output: Ereignis (Event 1 = Zugang erlaubt ; Event 0 = Zugang verweigert ; Event 2 = Unbekannt ; Event 3 = Raum unbekannt)

# Log() Protokolliert ein Ereignis
# Input: event, key, roomNumber, name  | Output:

# Query() Stellt eine Abfrage an den SQL-Server
# Input:  | Output: Ergebnis der Abfrage

# GetLogs() Holt alle Logs
# Input:  | Output: Logs

# DelLogs() Loescht alle Logs
# Input:  | Output:

# GetIP() Findet die IP-Adresse des Netzwerkadapters
# Input:  | Output: IP

# SetIP() Schreibt die IP-Addresse in die SQL-Datenbank
# Input:  | Output:

# CheckManualAccess() Prueft ob ein Raum durch das Interface geoeffnet werden soll
# Input:  | Output: True/False

# ResetOpenFlag() Setz die openFlag auf 0
# Input:  | Output:

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
	def CheckPermission(self, key, roomNumber):
		User = self.Query('SELECT * FROM Users WHERE tagID = %s', key)
		Room = self.Query('SELECT * FROM Rooms WHERE roomNr = %s', roomNumber)
		event = 2
		if(User and Room):
			# User[6] = Prio; Room[6] = Prio
			if(User[6] >= Room[6]):
				# Event 1 = Zugang erlaubt
				event = 1
				# Event protokollieren	
				self.Log(event, key, roomNumber, User[1])
			else:
				# Event 0 = Zugang verweigert
				event = 0
				# Event protokollieren	
				self.Log(event, key, roomNumber, User[1])
		elif(not Room):
			# Event 3 = Raum unbekannt
			event = 3
		else:
			# Event 2 = Unbekannt
			event = 2
			self.Log(event, key, roomNumber, 'UNBEKANNT')	
		return event

	# Event protokollieren
	def Log(self, event, key, roomNumber, name):
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute('INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())', (event, key, roomNumber, name))
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

	# Log abfragen
	def GetLogs(self):
		result = False
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute('SELECT * FROM Logs')
		result = curser.fetchall()
		db.commit()
		db.close()
		return result

	# Logs loeschen
	def DelLogs(self):
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute('DELETE FROM Logs')
		db.commit()
		db.close()

	# Eigene IP finden
	def GetIP(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			IP = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'eth0'[:15]))[20:24])
			#IP = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'wlan0'[:15]))[20:24])
		except:
			IP = 'NULL'
		finally:
			return IP

	# Schreibt eigene IP in die Datenbank
	def SetIP(self, roomNr):
		IP = self.GetIP()
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute('UPDATE Rooms SET IP = %s WHERE RoomNr = %s', (IP ,roomNr))
		db.commit()
		db.close()

	# Prueft ob openFlag gesetzt wurde
	def CheckManualAccess(self, roomNumber):
		Room = self.Query('SELECT * FROM Rooms WHERE roomNr = %s', roomNumber)
		if(Room):
			# Room[7] = openFlag
			if(Room[7] == 1):
				self.ResetOpenFlag(roomNumber)
				self.Log(1, 0, roomNumber, 'WEB-INTERFACE')
				return True

	# Setzt openFlag des Raums auf 0
	def ResetOpenFlag(self, roomNr):
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute('UPDATE Rooms SET openFlag = 0 WHERE roomNr = %s', (roomNr,))
		db.commit()
		db.close()


# ================================================================================
#				Klasse: LED
# Steuert die LED

# Start()
# Input:  | Output:

# Blackout()
# Input:  | Output:

# Blau() 
# Input: | Output:

# Gruen() 
# Input: | Output:

# Rot() 
# Input: | Output:

# RotBlink() 
# Input: | Output:

# Orange() 
# Input: | Output:

#  ================================================================================

class LED:
	def __init__(self):
		self.LED_1_COUNT      = 1      # Number of LED pixels.
		self.LED_1_PIN        = 12      # GPIO pin connected to the pixels (must support PWM! GPIO 13 and 18 on RPi 3).
		self.LED_1_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
		self.LED_1_DMA        = 10      # DMA channel to use for generating signal (Between 1 and 14)
		self.LED_1_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
		self.LED_1_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
		self.LED_1_CHANNEL    = 0       # 0 or 1
		self.LED_1_STRIP      = ws.SK6812_STRIP_GRBW
		self.led1 = Adafruit_NeoPixel(self.LED_1_COUNT, self.LED_1_PIN, self.LED_1_FREQ_HZ, self.LED_1_DMA, self.LED_1_INVERT, self.LED_1_BRIGHTNESS, self.LED_1_CHANNEL, self.LED_1_STRIP)
		self.led1.begin()

	def StartUp(self):
		for i in range(8):
			self.led1.setPixelColor(0, Color(0, 0, 64))
			self.led1.show()
			time.sleep(.1)
			self.led1.setPixelColor(0, Color(0, 0, 16))
			self.led1.show()
			time.sleep(.1)

	def Blackout(self):
		self.led1.setPixelColor(0, Color(0,0,0))
		self.led1.show()

	def Blau(self):
		self.led1.setPixelColor(0, Color(0, 0, 32))
		self.led1.show()

	def Gruen(self):
		self.led1.setPixelColor(0, Color(0, 128, 0))
		self.led1.show()

	def Rot(self):
		self.led1.setPixelColor(0, Color(128, 0, 0))
		self.led1.show()
		time.sleep(1)

	def RotBlink(self):
		for i in range(8):
			self.led1.setPixelColor(0, Color(128, 0, 0))
			self.led1.show()
			time.sleep(.1)
			self.led1.setPixelColor(0, Color(16, 0, 0))
			self.led1.show()
			time.sleep(.1)

	def Orange(self):
		self.led1.setPixelColor(0, Color(32, 24, 0))


# ================================================================================
#				Klasse: Mail
# Verschickt Fehlermeldungen und Protokolle

# SendArchive
# Input: Logs ;  Betreff | Output:

# SendErrorRestart() 
# Input: Error ;  Betreff | Output:

# SendError() 
# Input: Error ;  Betreff | Output:

# ================================================================================
class Mail:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('/home/pi/Zerberus/config.ini')
		self.targetaddress = config.get('EMAIL', 'ZielAdresse')
		self.originAddress = config.get('EMAIL', 'QuellAdresse')
		self.password = config.get('EMAIL', 'Passwort')
		self.port = config.getint('EMAIL', 'Port')
		self.smtp = config.get('EMAIL', 'smtpAdresse')

	# Email senden
	def SendArchive(self, logs, subject):

		book = xlwt.Workbook()
		sheet1 = book.add_sheet('sheet1')

		for x,tuple in enumerate(logs):
			for y,item in enumerate(tuple):
				print(x)
				print(y)
				sheet1.write(x,y,str(item))

		name = "random.xls"
		book.save(name)
		book.save(TemporaryFile())


		message = MIMEMultipart()
		message.attach(MIMEText(subject))

		part = MIMEBase('application', "octet-stream")
		part.set_payload(open("random.xls", "rb").read())
		encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="random.xls"')
		message.attach(part)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.originAddress, self.password)
		server.sendmail(self.originAddress, self.targetaddress, message.as_string())









	# Error per Email senden
	def SendError(self, error, subject):
		error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
		message = 'Subject: {}\n\n{}'.format(subject, error)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.originAddress, self.password)
		server.sendmail(self.originAddress, self.targetaddress, message)

	# Error per Email senden
	def SendError(self, error, subject):
		message = 'Subject: {}\n\n{}'.format(subject, error)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.originAddress, self.password)
		server.sendmail(self.originAddress, self.targetaddress, message)


# ================================================================================
#				ausfuehren als __main__
# ================================================================================
if __name__ == '__main__':
	try:
		main()

	except Exception as error:
		print(error)
		mail = Mail()
		mail.SendErrorRestart(error, 'ZERBERUS ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)

# ================================================================================
#				Funktionen fuer externe Anwendungen
# ================================================================================
def Archive():
	try:
		sql1 = SQL()
		mail1 = Mail()
		logs = sql1.GetLogs()
		mail1.SendArchive(logs, 'Logarchiv:')
		#sql1.DelLogs()

	except Exception as error:
		mail1 = Mail()
		mail1.SendError(error, 'ARCHIVE ERROR:')

def Manual():
	try:
		door1 = DoorControl()
		door1.ManualUnlock()

	except Exception as error:
		mail1 = Mail()
		mail1.SendError(error, 'ARCHIVE ERROR:')