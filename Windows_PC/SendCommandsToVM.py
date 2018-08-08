#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, time

TCP_IP = '127.0.0.1'
TCP_PORT = 51951
BUFFER_SIZE = 1024

COMMANDS = ["crazyflie3$Register", "crazyflie3$TakeOff$3$3", "crazyflie3$UP", "crazyflie3$UP", "crazyflie3$LEFT", "crazyflie3$LEFT", "crazyflie3$Land", "crazyflie3$UnRegister"]

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True: # Keep trying to establish a connection with the VM
		try:
			s.connect((TCP_IP, TCP_PORT))
			break
		except:
			print "No response from {}:{}, Retry in 5 seconds...".format(TCP_IP,TCP_PORT)
			time.sleep(5)
	s.settimeout(5)  # socket operation will timeout after 2secs
	for command in COMMANDS:
		s.send(command)
		try:
			data = s.recv(BUFFER_SIZE)
			if data == "OK":
				print "Send: '{}' received: '{}'".format(command,data)
			elif data == "FAILED":
				print "Executing '{}' failed".format(command)
			elif data == "FORMAT":
				print "Command '{}' rejected by the VM - Invalid format".format(command)
			elif data == "INVALID":
				print "Command '{}' rejected by the VM - Invalid parameters".format(command)
			elif len(data) == 0:
				print "The client at the VM died"
				exit(1)
			else:
				print "Unknown response '{}' from the VM for '{}'".format(data,command)
		except socket.timeout:
			print "timeout" 
			exit(1)
		time.sleep(1)
	s.close()

if __name__ == '__main__':
	main()
