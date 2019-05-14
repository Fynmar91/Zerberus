#!/usr/bin/env python

import socket
import Zerberus

TCP_IP = '10.1.1.41'
TCP_PORT = 8080
BUFFER_SIZE = 20 # Normally 1024, but I want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print ('Connection address:', addr)
while 1:
	data = conn.recv(BUFFER_SIZE)
	if not data: break
	Zerberus.Manual()
	print ("received data:", data)
	conn.send(data)  # echo
conn.close()