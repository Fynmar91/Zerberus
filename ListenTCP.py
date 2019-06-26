#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	TCP Empfangen v1.1
#	Yannik Seitz 15.05.19

import socket
import fcntl
import struct
import Zerberus
import logging
import subprocess



def main():
	s1 = Socket()
	while True:
		s1.Receive()
	conn.close()

class Socket:
	def __init__(self):
		self.TCP_IP = False
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_IP = socket.inet_ntoa(fcntl.ioctl(self.s.fileno(), 0x8915, struct.pack('256s', 'eth0'[:15]))[20:24])
		#self.TCP_IP = socket.inet_ntoa(fcntl.ioctl(self.s.fileno(), 0x8915, struct.pack('256s', 'wlan0'[:15]))[20:24])
		self.TCP_PORT = 8080
		self.BUFFER_SIZE = 20
		print(self.TCP_IP)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.TCP_IP, self.TCP_PORT))

	def Receive(self):
		self.s.listen(1)
		self.conn, self.addr = self.s.accept()
		data = self.conn.recv(self.BUFFER_SIZE)
		if data:
			print(data)
			Zerberus.Manual()
			self.conn.send(data)


if __name__ == '__main__':
	try:
		main()

	except Exception as error:
		print(error)
		subprocess.call('/home/pi/Zerberus/Restart', shell=True)
		logging.basicConfig(filename='/home/pi/Zerberus/error.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
		logger = logging.getLogger(__name__)
		logger.error(error)
