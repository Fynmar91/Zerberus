#!/usr/bin/env python
#	Yannik Seitz 20.03.19
#	FS2V Tuerzugangs-Projekt
#	Diese Datei beinhaltet alle selbst geschriebenen GPIO-Funktionen

import RPi.GPIO as GPIO
import SimpleMFRC522
import time

	# GPIO-Eingaenge konfigurieren
def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17,GPIO.OUT)
	GPIO.setup(18,GPIO.OUT)
	GPIO.setup(22,GPIO.OUT)
	GPIO.output(18,GPIO.HIGH)



	# RFID lesen mit SimpleMFRC522-Funktion
def read():
	reader = SimpleMFRC522.SimpleMFRC522()
	try:
		id, text = reader.read()
		print("RFID.read() %s " % id)
	finally:
		return id

	# Rote LED
def errorSignal():
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(17,GPIO.OUT)
	print("LED on")
	GPIO.output(17,GPIO.HIGH)
	time.sleep(1)
	print("LED off")
	GPIO.output(17,GPIO.LOW)

        # Gelbe LED an
def onSignal():
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(22,GPIO.OUT)
	print("LED on")
	GPIO.output(22,GPIO.HIGH)

        # Gelbe LED aus
def offSignal():
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(22,GPIO.OUT)
	print("LED off")
	GPIO.output(22,GPIO.LOW)

	# Tuer oeffnen
def openDoor():
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(18,GPIO.OUT)
	print("Relay on")
	GPIO.output(18,GPIO.LOW)
	time.sleep(3)
	print("Relay off")
	GPIO.output(18,GPIO.HIGH)
