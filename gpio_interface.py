#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	GPIO Interface v1.3
#	Yannik Seitz 11.04.19
#	Diese Datei beinhaltet alle Funktionen die den GPIO steuern

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
	finally:
		return id

	# Rote LED
def ErrEvent0():
	for i in range(10):
		GPIO.output(17,GPIO.HIGH)
		time.sleep(0.05)
		GPIO.output(17,GPIO.LOW)
		time.sleep(0.05)


def ErrEvent2():
	GPIO.output(17,GPIO.HIGH)
	time.sleep(1)
	GPIO.output(17,GPIO.LOW)

        # Gelbe LED an
def onSignal():
	GPIO.output(22,GPIO.HIGH)

        # Gelbe LED aus
def offSignal():
	GPIO.output(22,GPIO.LOW)

	# Tuer oeffnen
def openDoor():
	GPIO.output(18,GPIO.LOW)
	for i in range(5):
		GPIO.output(22,GPIO.HIGH)
		time.sleep(0.05)
		GPIO.output(22,GPIO.LOW)
		time.sleep(0.05)
	time.sleep(3)
	GPIO.output(18,GPIO.HIGH)
	onSignal()
