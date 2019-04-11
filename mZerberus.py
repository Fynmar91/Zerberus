#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	manual Zerberus v1.1
#	Yannik Seitz 11.04.19
#	Dieses Programm wird durch den mWatchdog-Dienst gestartet und verarbeitet einkommende SQL-Oeffnungsanfragen
#	GPIO- und SQL-Aufgaben sind in zwei andere Dateinen ausgelagert

import sql_interface
import gpio_interface
import time

	# Prueft ob openFlag gesetzt wurde
def checkManualOpen(SQL, room_number):
	Room = sql_interface.readRoom(SQL, room_number)
	if(Room):
		if(Room[7] == 1):	# Room[7] = Rooms::openFlag
			gpio_interface.openDoor()
			sql_interface.resetOpenFlag(SQL, room_number)

	# Endlose Schleife mit Pause
def start(SQL, room_number):
	while True:
		checkManualOpen(SQL, room_number)
		time.sleep(1)
