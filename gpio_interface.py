#!/usr/bin/env python
#	Yannik Seitz 20.03.19
#	FS2V Tuerzugangs-Projekt 
#	Diese Datei beinhaltet alle selbst geschriebenen GPIO-Funktionen

import RPi.GPIO as GPIO
import SimpleMFRC522
import time

	# RFID lesen mit SimpleMFRC522-Funktion
def read():
	reader = SimpleMFRC522.SimpleMFRC522()
	try:
		id, text = reader.read()
		print("RFID.read() %s " % id)
	finally:
		GPIO.cleanup()
	return id

	# Rote LED
def errorSignal():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17,GPIO.OUT)
	print("LED on")
	GPIO.output(17,GPIO.HIGH)
	time.sleep(1)
	print("LED off")
	GPIO.output(17,GPIO.LOW)
	GPIO.cleanup()
	

	# Tuer oeffnen
def openDoor():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18,GPIO.OUT)
	print("Relay on")
	GPIO.output(18,GPIO.LOW)
	time.sleep(3)
	print("Relay off")
	GPIO.output(18,GPIO.HIGH)
	GPIO.cleanup()
