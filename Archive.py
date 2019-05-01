#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Archive v1.1
#	Yannik Seitz 30.04.19
#	Dieses Programm

import time
import subprocess
import MailControl
import SqlControl

def main():
	sql = SqlControl.SQL()
	mail = MailControl.Mail()
	logs = sql.GetLogs()
	mail.SendArchive(logs, 'Logarchiv:')
	sql.DelLogs()

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = mail_class.Mail()
		mail.SendError(error, 'ARCHIVE ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)