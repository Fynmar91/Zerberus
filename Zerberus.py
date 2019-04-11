#!/usr/bin/env python
#	Yannik Seitz 20.03.19
#	Zerberus FS2V Tuerzugangs-Projekt
#	Programm wird durch einen Watchdog-Dienst gestartet und verarbeitet einkommende RFID-Oeffnungsanfragen
#	GPIO- und SQL-Aufgaben sind in zwei andere Dateinen ausgelagert
#	Raumnummer soll aus einer Config-Datei ausgelesen werden

import gpio_interface
import sql_interface
import time

	# Ruft Logging-Funktion auf
def log(event, tagID, User, SQL, room_number):
	if(event == 1):		# Zugang erlaubt
		sql_interface.writeLog1(event, tagID, SQL, room_number, User)
	elif(event == 0):	# Zugang verweigert
		sql_interface.writeLog0(event, tagID, SQL, room_number, User)
	elif(event == 2):	# RFID unbekannt
		sql_interface.writeLog2(event, tagID, SQL, room_number)
	else:
		print("log() error")

	# Prueft Zugangsbrechtigung
def checkAccess(userPrio, roomPrio):
	print("%s >= %s" % (userPrio, roomPrio))
	if(userPrio >= roomPrio):
		print("Zugang Event 1")	# Zugang erlaubt
		return 1
	else:
		print("NEIN Event 0")	# Zugang verweigert
		return 0

	# Sucht Nutzer und Raumdaten, prueft Berechtigung und oeffnet evtl die Tuer
def process(tagID, SQL, room_number):
	User = sql_interface.readUser(tagID, SQL)
	Room = sql_interface.readRoom(SQL, room_number)
	if(User and Room):
		event = checkAccess(User[6], Room[6])
	elif(User == false and Room):
		print("Unbekannt Event 2")	# RFID unbekannt
		event = 2
	else:
		print("process() error")	# Unvorhergesehner moeglicher Fehler?
		event = 3
	log(event, tagID, User, SQL, room_number)	# Logging
	if(event == 1):
		gpio_interface.openDoor()	# Tuer oeffnen
	else:
		gpio_interface.errorSignal()	# Kein Zugang, rote LED

	# Sucht nach RFID Tag und ruft Prozess zur Verarbeitung auf
def scan(SQL, room_number):
	tagID = gpio_interface.read()
	if(tagID):
		process(tagID, SQL, room_number)


	# Endlose Schleife mit Pause
def start(SQL, room_number):
	while True:
		scan(SQL, room_number)
		time.sleep(1)
