#!/usr/bin/env python

import socket

def main():
	s1 = Socket()	
	s1.Send()


class Socket:
	def __init__(self):
		self.TCP_IP = '192.168.137.1'
		self.TCP_PORT = 8080
		self.BUFFER_SIZE = 1024

	def Send(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.MESSAGE = "Hello, World!".encode()
		self.s.connect((self.TCP_IP, self.TCP_PORT))
		self.s.send(self.MESSAGE)
		data = self.s.recv(self.BUFFER_SIZE)
		conn.close()


if __name__ == '__main__':
		main()
