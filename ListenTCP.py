#!/usr/bin/env python

import socket
import fcntl
import struct
import Zerberus



def main():
	s1 = Socket()
	while True:
		s1.Receive()
	conn.close()

class Socket:
	def __init__(self):
		self.TCP_IP = False
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#	self.TCP_IP = socket.inet_ntoa(fcntl.ioctl(self.s.fileno(), 0x8915, struct.pack('256s', 'eth0'[:15]))[20:24])
		self.TCP_IP = socket.inet_ntoa(fcntl.ioctl(self.s.fileno(), 0x8915, struct.pack('256s', 'wlan0'[:15]))[20:24])
		self.TCP_PORT = 8080
		self.BUFFER_SIZE = 20

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.TCP_IP, self.TCP_PORT))
		self.s.listen(1)
		self.conn, self.addr = self.s.accept()

	def Receive(self):
		data = self.conn.recv(self.BUFFER_SIZE)
		if data: 
			Zerberus.Manual()
			# echo
			self.conn.send(data)


if __name__ == '__main__':
	main()
