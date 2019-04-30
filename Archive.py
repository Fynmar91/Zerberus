#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Archive v1.1
#	Yannik Seitz 30.04.19
#	Dieses Programm

import time
import subprocess
import class_mail
import class_sql

def main():
	sql = class_sql.SQL()
	mail = class_mail.Mail()
	logs = sql.GetLogs()
	mail.SendArchive(logs, 'Logarchiv:')

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = mail_class.Mail()
		mail.SendError(error, 'ARCHIVE ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)