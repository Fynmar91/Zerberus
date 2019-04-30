#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Door Klasse v1.2
#	Yannik Seitz 30.04.19
import time
import ConfigParser
import MySQLdb
import RPi.GPIO as GPIO
import class_sql

class Door:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.number = config.get('ROOM', 'Raumnummer')
		self.sql = class_sql.SQL()
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM) # GPIO in BCM mode
		GPIO.setup(17,GPIO.OUT) # Rot
		GPIO.setup(18,GPIO.OUT) # Tueroeffner
		GPIO.setup(22,GPIO.OUT) # Gruen
		GPIO.output(18,GPIO.HIGH) # Relais schliesst bei low

	def Open(self, key):
		event = self.sql.CheckPermission(key, self.number) # Zungangsberechtigung kontrollieren
		if(event == 1):
			self.Granted() # Event 1; Zugang erlaubt; Tuer oeffnen
		elif(event == 0):
			self.Denied() # Event 0; Kein Zugang; rote LED blinkt
		elif(event == 2):
			self.Unknown() # Event 2; Unbekannt; rote LED

	def ManualOpen(self): # Prueft ob openFlag gesetzt wurde
		if(self.sql.CheckManualAccess(key, self.number)):
			self.Granted() # Tuer oeffnen


	def Granted(self): # Tuer oeffnen
		GPIO.output(18,GPIO.LOW)
		for i in range(10):
			GPIO.output(22,GPIO.HIGH)
			time.sleep(0.2)
			GPIO.output(22,GPIO.LOW)
			time.sleep(0.1)
		GPIO.output(18,GPIO.HIGH)

	def Unknown(self): # Unbekannt; rote LED
		GPIO.output(17,GPIO.HIGH)
		time.sleep(1)
		GPIO.output(17,GPIO.LOW)

	def Denied(self): # Kein Zugang; rote LED blinkt
		for i in range(10):
			GPIO.output(17,GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(17,GPIO.LOW)
			time.sleep(0.05)
