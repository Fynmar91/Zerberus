#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Zerberus v1.1
#	Yannik Seitz 30.04.19
#	Dieses Programm verarbeitet eingelesene RFID-tagIDs und ueberprueft ob sie zugangsberechtigt sind
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und ein Neustart durchgefuehrt

import time
import subprocess
import RPi.GPIO as GPIO
import SimpleMFRC522
import mail_class
import door_class

def main():
	GPIOsetup()
	door = door_class.Door()
	while True:
		event = False
		key = False
		name = False
		GPIO.output(22,GPIO.HIGH) # Status LED Gruenan
		key = ReadRFID() # RFID-Karte einlesen
		event, name = door.Check(key) # Zungangsberechtigung kontrollieren
		door.Log(event, key, name)	# Event protokollieren
		if(event == 1):
			door.Open()			# Event 1; Zugang erlaubt; Tuer oeffnen
		elif(event == 0):
			door.Prohibited()	# Event 0; Kein Zugang; rote LED blinkt
		elif(event == 2):
			door.Unknown()		# Event 2; Unbekannt; rote LED

def manual():
	GPIOsetup()
	door = Door()
	while True:
		door.CheckManualOpen()
		time.sleep(5)


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

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = mail_class.Mail()
		mail.SendError(error, 'ZERBERUS ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
else:
	try:
		manual()

	except Exception as error:
		mail = mail_class.Mail()
		mail.SendError(error, 'PUPPY ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
