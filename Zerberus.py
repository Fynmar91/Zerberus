#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Zerberus v1.3
#	Yannik Seitz 30.04.19
#	Dieses Programm verarbeitet eingelesene RFID-tagIDs und ueberprueft ob sie zugangsberechtigt sind
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und ein Neustart durchgefuehrt

import time
import subprocess
import RPi.GPIO as GPIO
import SimpleMFRC522
import class_mail
import class_door

def main():
	door = class_door.Door()
	while True:
		key = False
		GPIO.output(22,GPIO.HIGH) # Status LED Gruen
		key = ReadRFID() # RFID-Karte einlesen
		if(key):
			door.Open(key)
		else:
			pass

def manual():
	door = class_door.Door()
	while True:
		door.ManualOpen()
		time.sleep(5)

def ReadRFID():	# RFID-Karte einlesen
	reader = SimpleMFRC522.SimpleMFRC522()
	try:
		key = reader.read_id()
	finally:
		return key

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = class_mail.Mail()
		mail.SendError(error, 'ZERBERUS ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
else:
	try:
		manual()

	except Exception as error:
		mail = class_mail.Mail()
		mail.SendError(error, 'PUPPY ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
