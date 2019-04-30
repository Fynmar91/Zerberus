import time
import subprocess
import smtplib
import ssl
import RPi.GPIO as GPIO
import SimpleMFRC522
import MySQLdb
import ConfigParser

def main():
	GPIOsetup()
	GPIO.output(22,GPIO.HIGH) # Status LED Gruen an
	door = Door()
	while(1):
		key = ReadRFID() # RFID-Karte einlesen
		event, name = door.Check(key) # Zungangsberechtigung kontrollieren
		door.Log(event, key, name)	# Event protokollieren
		if(event == 1):
			door.Open()			# Event 1; Zugang erlaubt; Tuer oeffnen
		elif(event == 0):
			door.Prohibited()	# Event 0; Kein Zugang; rote LED blinkt
		elif(event == 2):
			door.Unknown()		# Event 2; Unbekannt; rote LED


def GPIOsetup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM) # GPIO in BCM mode
	GPIO.setup(17,GPIO.OUT) # Rot
	GPIO.setup(18,GPIO.OUT)	# Tueroeffner
	GPIO.setup(22,GPIO.OUT)	# Gruen
	GPIO.output(18,GPIO.HIGH) # Relais schliesst bei low

def ReadRFID():	# RFID-Karte einlesen
	reader = SimpleMFRC522.SimpleMFRC522()
	try:
		key, text = reader.read()
	finally:
		return key

class Door:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.ip = config.get('SQL', 'IP')
		self.user = config.get('SQL', 'Nutzer')
		self.password = config.get('SQL', 'Passwort')
		self.database = config.get('SQL', 'DatenbankName')
		self.number = config.get('ROOM', 'Raumnummer')

	def Check(key):	# Zungangsberechtigung kontrollieren
		User = Query("SELECT * FROM Users WHERE tagID = %s", key)
		Room = Query("SELECT * FROM Rooms WHERE roomNr = %s", self.number)
		if(User and Room):
			if(User[6] >= Room[6]):
				return 1, User[1]	# Event 1; Zugang erlaubt
			else:
				return 0, User[1]	# Event 0; Zugang verweigert
		elif(User == False and Room):
			return 2, 'Unbekannt'	# Event 2; Unbekannt

	def Log(event, key, name):	# Event protokollieren
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("INSERT INTO Logs (event, tagID, roomNr, userName, date, time) VALUES (%s, %s, %s, %s, CURDATE(), CURRENT_TIME())", (event, key, self.number, name))
		db.commit()
		db.close()

	def Open():	# Tuer oeffnen
		GPIO.output(18,GPIO.LOW)
		for i in range(10):
			GPIO.output(22,GPIO.HIGH)
			time.sleep(0.2)
			GPIO.output(22,GPIO.LOW)
			time.sleep(0.1)
		GPIO.output(18,GPIO.HIGH)
		GPIO.output(22,GPIO.HIGH)

	def Unknown(): # Unbekannt; rote LED
		GPIO.output(17,GPIO.HIGH)
		time.sleep(1)
		GPIO.output(17,GPIO.LOW)

	def Prohibited():	# Kein Zugang; rote LED blinkt
		for i in range(10):
			GPIO.output(17,GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(17,GPIO.LOW)
			time.sleep(0.05)

	def Query(query, var): # SQL Anfrage
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


class Mail:
	def __init__(self, error):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.address = config.get('EMAIL', 'Adresse')
		self.password = config.get('EMAIL', 'Passwort')
		self.port = config.getint('EMAIL', 'Port')
		self.smtp = config.get('EMAIL', 'smtpAdresse')
		self.error = error

	def Send(): # Email senden
		subject = 'ZERBERUS ERROR:'
		error = '{}\n\n{}'.format(self.error,'!!Geraet wird neu gestartet!!')
		message = 'Subject: {}\n\n{}'.format(subject, error)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)


if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = Mail(error)
		mail.Send()
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
	