#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logger, socket, time

cf_logger = logger.get_logger(__name__) # debug(), info(), warning(), error(), exception(), critical()

DEFAULT_TCP_IP = "127.0.0.1"
DEFAULT_TCP_PORT = 51951
DEFAULT_BUFFER_SIZE = 1024

class DronesControllerAPI(object):
	def __init__(self, ip=DEFAULT_TCP_IP, port=DEFAULT_TCP_PORT, buffer_size=DEFAULT_BUFFER_SIZE):
		self._tcp_ip = ip
		self._tcp_port = port
		self._buffer_size = buffer_size
###################################################################################################
	def connect(self): # Return True on success and False otherwise
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		for retry in range(5): # Keep trying to establish a connection with the VM
			try:
				self._socket.connect((self._tcp_ip, self._tcp_port))
				self._socket.settimeout(10) # Socket operation will timeout after 5 secs # TODO - Should go back to 5 when the game development enter stage B
				return True
			except:
				cf_logger.error("Failure {}/5, No response from {}:{}, Trying again in 5 seconds...".format(retry + 1, self._tcp_ip, self._tcp_port))
				time.sleep(5)
		return False

	def disconnect(self):
		self._socket.close()
###################################################################################################
	def get_world_size():
		x = y = 0
		return [x, y]

	def get_objects():
		return ["names_0", "names_1", "names_2"]

	def get_object_position(object_name):
		x = y = z = 0
		return [x, y, z]

	def move_drone(drone_name, direction_vector) # direction_vector = [x, y]
		pass

	def goto(pos): # pos = [x, y]
		pass

	def take_off():
		pass

	def land():
		pass

	def battery_status():
		return 0
###################################################################################################
#	def send(self, command): # Return 0 on success, 1 if the Vm report on an error and -1 if the connection is closed
#		try:
#			self._socket.send(command.encode())
#		except socket.error as e:
#			cf_logger.critical("Socket error: {}".format(e))
#			return -1
#		try:
#			data = self._socket.recv(self._buffer_size).decode()
#			if data == "OK":
#				cf_logger.debug("Send: '{}' received: '{}'".format(command, data))
#				return 0
#			elif data == "FAILED":
#				cf_logger.error("Executing '{}' failed".format(command))
#			elif data == "FORMAT":
#				cf_logger.error("Command '{}' rejected by the VM - Invalid format".format(command))
#			elif data == "INVALID":
#				cf_logger.error("Command '{}' rejected by the VM - Invalid parameters".format(command))
#			elif len(data) == 0:
#				cf_logger.critical("The client at the VM died")
#				return -1
#			else:
#				cf_logger.error("Unknown response '{}' from the VM for '{}'".format(data, command))
#		except socket.timeout:
#			cf_logger.critical("Timeout")
#			return -1
#		return 1
###################################################################################################

if __name__ == "__main__":
	print("This is not the way to do it...")
