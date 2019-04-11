#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	manual Watchdog v1.1
#	Yannik Seitz 11.04.19
#	Dieses Programm startet das mZerberus-Programm und berwacht dieses. 
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und ein Neustart durchgeführt.

import time
import subprocess
import smtplib
import ssl

import mZerberus
import ConfigParser

def ReadConfig():

	#Config einlesen
	config = ConfigParser.RawConfigParser()
	config.read('config.ini')

	#SQL config
	sql_ip = config.get('SQL', 'ip')
	sql_user = config.get('SQL', 'user')
	sql_password = config.get('SQL', 'password')
	sql_database = config.get('SQL', 'database')

	#MAIL config
	mail_address = config.get('EMAIL', 'address')
	mail_password = config.get('EMAIL', 'password')
	mail_port = config.getint('EMAIL', 'port')
	mail_smtp = config.get('EMAIL', 'smtp')

	#ROOM config
	room_number = config.get('ROOM', 'number')

	SQL = (sql_ip, sql_user, sql_password, sql_database)
	MAIL = (mail_address, mail_password, mail_port, mail_smtp)

	return SQL, MAIL, room_number

def Send(MAIL, subject, error):
	port = MAIL[2]
	smtp_server = MAIL[3]
	sender_email = MAIL[0]
	receiver_email = MAIL[0]
	password = MAIL[1]
	error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
	message = 'Subject: {}\n\n{}'.format(subject, error)

	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL(smtp_server, port)
	server.login(sender_email, password)
	server.sendmail(sender_email, receiver_email, message)

try:
	SQL, MAIL, room_number = ReadConfig()
	mZerberus.start(SQL, room_number)


except Exception as error:
	Send(MAIL, 'ZERBERUS: ERROR MANUAL WATCHDOG', error)
	subprocess.call('/home/pi/Zerberus/restart', shell=True)
