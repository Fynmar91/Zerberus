#!/usr/bin/env python

import time
import subprocess
import smtplib
import ssl
import Manual

def Send(subject, error):
	port = 465
	smtp_server = "smtp.gmail.com"
	sender_email = "zerberus.fs2v@gmail.com"
	receiver_email = "zerberus.fs2v@gmail.com"
	password = "rassi123"
	message = 'Subject: {}\n\n{}'.format(subject, error)

	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL(smtp_server, port)
	server.login(sender_email, password)
	server.sendmail(sender_email, receiver_email, message)

try:
	Send("Manual", "started")
	Manual.start()


except Exception as error:
	Send("Error", error)
	subprocess.call("/home/pi/Zerberus/restart", shell=True)

