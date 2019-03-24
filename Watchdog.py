#!/usr/bin/env python

import time
import subprocess
import smtplib
import ssl
import AccessControl

def Send():
	print('send')
	port = 465
	smtp_server = "smtp.gmail.com"
	sender_email = "zerberus.fs2v@gmail.com"
	receiver_email = "zerberus.fs2v@gmail.com"
	password = "rassi123"
	message = 'Subject: {}\n\n{}'.format('Go: ', 'go')

	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL(smtp_server, port)
	server.login(sender_email, password)
	server.sendmail(sender_email, receiver_email, message)

print("1")
try:
	print('send1')
	Send()
	#AccessControl.start()

except Exception as error:
	Send()
	#subprocess.call("/home/pi/Zerberus/rebootPi.sh", shell=True)
