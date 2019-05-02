#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Archive v1.2
#	Yannik Seitz 01.05.19
#	

import time
import subprocess
import smtplib
import ssl
import MySQLdb
import ConfigParser

def main():
	sql = SQL()
	mail = Mail()
	logs = sql.GetLogs()
	mail.SendArchive(logs, 'Logarchiv:')
	sql.DelLogs()

class SQL:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('config.ini')
		self.ip = config.get('SQL', 'IP')
		self.user = config.get('SQL', 'Nutzer')
		self.password = config.get('SQL', 'Passwort')
		self.database = config.get('SQL', 'DatenbankName')

	def GetLogs(self): # SQL Anfrage
		result = False
		db = MySQLdb.connect(self.ip, self.user, self.password, self.database)
		curser = db.cursor()
		curser.execute("SELECT * FROM Logs")
		result = curser.fetchall()
		db.commit()
		db.close()
		return result

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

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = Mail()
		mail.SendError(error, 'ARCHIVE ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)