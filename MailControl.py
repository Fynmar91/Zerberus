#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Mail Klasse v1.1
#	Yannik Seitz 30.04.19

import ConfigParser
import smtplib
import ssl

class Mail:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.address = config.get('EMAIL', 'Adresse')
		self.password = config.get('EMAIL', 'Passwort')
		self.port = config.getint('EMAIL', 'Port')
		self.smtp = config.get('EMAIL', 'smtpAdresse')

	def SendArchive(self, logs, subject): # Email senden
		list = ''
		for tuple in logs:
			list = '{}\n\n{}'.format(list, tuple)
		message = 'Subject: {}\n\n{}'.format(subject, list)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)

	def SendError(self, error, subject): # Email senden
		error = '{}\n\n{}'.format(error,'!!Geraet wird neu gestartet!!')
		message = 'Subject: {}\n\n{}'.format(subject, error)

		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL(self.smtp, self.port)
		server.login(self.address, self.password)
		server.sendmail(self.address, self.address, message)