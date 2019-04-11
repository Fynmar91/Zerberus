#!/usr/bin/env python
#	Yannik Seitz 20.03.19
#	Zerberus FS2V Tuerzugangs-Projekt

import sql_interface
import gpio_interface
import time

	# Prueft ob openFlag gesetzt wurde
def checkManualOpen():
	Room = sql_interface.readRoom(SQL, room_number)
	if(Room):
		if(Room[7] == 1):
			print("Manual")
			gpio_interface.openDoor()
			sql_interface.resetOpenFlag(SQL, room_number)

	# Endlose Schleife mit Pause
def start(SQL, room_number):
	while True:
		checkManualOpen(SQL, room_number)
		time.sleep(1)
