#!/usr/bin/env python

import time
import subprocess
import smtplib
import ssl
import Manual

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

	return SQL, room_number

def Send(subject, error):
	port = 465
	smtp_server = 'smtp.gmail.com'
	sender_email = 'zerberus.fs2v@gmail.com'
	receiver_email = 'zerberus.fs2v@gmail.com'
	password = 'rassi123'
	error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
	message = 'Subject: {}\n\n{}'.format(subject, error)

	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL(smtp_server, port)
	server.login(sender_email, password)
	server.sendmail(sender_email, receiver_email, message)

try:
	Manual.start(SQL, room_number)


except Exception as error:
	Send('ERROR', error)
	subprocess.call('/home/pi/Zerberus/restart', shell=True)
