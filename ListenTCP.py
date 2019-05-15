#!/usr/bin/env python

import socket
import Zerberus

TCP_IP = '10.1.1.41'
TCP_PORT = 8080
# Normally 1024, but I want fast response
BUFFER_SIZE = 20

while True:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)
	conn, addr = s.accept()
	while True:
		data = conn.recv(BUFFER_SIZE)
		if not data: break
		Zerberus.Manual()
		# echo
		conn.send(data)
	conn.close()

class Socket:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('/home/pi/Zerberus/config.ini')
		self.IP = config.get('SERVER', 'IP')

# Eigene IP finden
	def get_ip(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			IP = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'eth0'[:15]))[20:24])
		except:
			IP = 'NULL'
		finally:
			return IP