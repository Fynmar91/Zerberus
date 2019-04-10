#!/usr/bin/env python

import time
import subprocess
import smtplib
import ssl

import Zerberus
import gpio_interface

#Config einlesen
import ConfigParser
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


def Send(subject, error):
	port = mail_port
	smtp_server = mail_smtp
	sender_email = mail_address
	receiver_email = mail_address
	password = mail_password
	error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
	message = 'Subject: {}\n\n{}'.format(subject, error)

	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL(smtp_server, port)
	server.login(sender_email, password)
	server.sendmail(sender_email, receiver_email, message)

try:
        gpio_interface.setup()
        gpio_interface.onSignal()
	Zerberus.start(sql_ip, sql_user, sql_password, sql_database, room_number)


except Exception as error:
	gpio_interface.offSignal()
	Send('ERROR:', error)
	subprocess.call('/home/pi/Zerberus/Restart', shell=True)
