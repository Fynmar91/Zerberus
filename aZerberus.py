#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	auto Zerberus v1.5
#	Yannik Seitz 11.04.19
#	Dieses Programm wird durch den aWatchdog-Dienst gestartet und verarbeitet einkommende RFID-Oeffnungsanfragen
#	GPIO- und SQL-Aufgaben sind in zwei andere Dateinen ausgelagert

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

	# Prueft Zugangsbrechtigung
def checkAccess(userPrio, roomPrio):
	if(userPrio >= roomPrio):
		return 1	# Event 1; Zugang erlaubt
	else:
		return 0	# Event 0; Zugang verweigert

	# Sucht Nutzer und Raumdaten, prueft Berechtigung und oeffnet evtl die Tuer
def process(tagID, SQL, room_number):
	User = sql_interface.readUser(tagID, SQL)
	Room = sql_interface.readRoom(SQL, room_number)
	if(User and Room):
		event = checkAccess(User[6], Room[6])	# User[6] = Users::Prio; Room[6] = Rooms::Prio
	elif(User == False and Room):
		event = 2
	log(event, tagID, User, SQL, room_number)	# Logging
	if(event == 1):
		gpio_interface.openDoor()	# Event 1; Zugang erlaubt; Tuer oeffnen
	elif(event == 0):
		gpio_interface.ErrEvent0()	# Event 0; Kein Zugang; rote LED
	elif(event == 2):
		gpio_interface.ErrEvent2()	# Event 0; Kein Zugang; rote LED

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
