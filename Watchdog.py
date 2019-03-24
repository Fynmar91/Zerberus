#!/usr/bin/env python

import time
import subprocess
import smtplib
import ssl

def Send(error):
	port = 465 
	smtp_server = "smtp.gmail.com"
	sender_email = "door.access.rassi@gmail.com"
	receiver_email = "door.access.rassi@gmail.com"
	password = "rassi123"
	message = 'Subject: {}\n\n{}'.format('Error:', error)
	
	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL(smtp_server, port)
	server.login(sender_email, password)
	server.sendmail(sender_email, receiver_email, message)


try:
	subprocess.call("/home/pi/FS2VdoorAccess/AccessControl.py", shell=True)

except Exception as error:
	Send(error)
	subprocess.call("/home/pi/FS2VdoorAccess/rebootPi.sh", shell=True)