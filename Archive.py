#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Archive v1.0
#	Yannik Seitz 30.04.19
#	Dieses Programm

import time
import subprocess
import mail_class
import door_class

def main():
	door = door_class.Door()
	mail = mail_class.Mail()
	logs = door.Query("SELECT * FROM Logs WHERE logID = %s", '*')
	mail.SendArchive(logs, 'Logarchiv:')

if __name__ == "__main__":
	try:
		main()

	except Exception as error:
		mail = mail_class.Mail()
		mail.SendError(error, 'ARCHIVE ERROR:')
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)