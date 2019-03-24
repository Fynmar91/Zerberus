#!/usr/bin/env python
#       Yannik Seitz 20.03.19
#       Zerberus FS2V Tuerzugangs-Projekt

import gpio_interface
import time

        # Prueft ob openFlag gesetzt wurde
def checkManualOpen():
        Room = checkRoom(roomNr)
        if(Room):
                if(Room[7] == 1):
                        print("Manual")
                        gpio_interface.openDoor()

        # Endlose Schleife mit Pause
def start():
        while True:
                checkManualOpen()
                time.sleep(1)

start()
