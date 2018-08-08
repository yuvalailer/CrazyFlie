#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, sys, time
#sys.path.insert(0,'/home/bitcraze/crazyflie_ws/src/crazyflie_ros/crazyflie_demo/scripts/') # XXX
if sys.version_info[0] > 2:
	print "If you can see this message, Then you are running Python 3 instead of 2"
	exit(0)
try:
	import crazyflie, rospy, tf
except:
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!!              OFFLINE mode is ON              !!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!! Warning, You don't have the crazyflie files  !!!!"
	print "!!!! Loading dummy files for testing purposes     !!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	from Simulator import crazyflie, rospy, tf

##### Editable part #####
TCP_IP = '127.0.0.1'
TCP_PORT = 51951
BUFFER_SIZE = 1024
WORLD_RANGE = {"X":[-0.7,1.0], "Y":[-0.9,0.5]}
WORLD_CELLS_COUNT = {"X":5, "Y":5}
FLIGHT_HEIGHT = 0.5
#########################

WORLD_STEPS = {"X":-1, "Y":-1} # Will be automaticly generated based on 'WORLD_RANGE' and 'WORLD_CELLS_COUNT'
WORLD_ORIGIN = {"X":-1, "Y":-1} # Will be automaticly generated
KNOWN_CRAZYFLIES = {}
VALID_DIRECTIONS = ["UP", "DOWN", "RIGHT", "LEFT"]
#		  0	      1		    2	       3       4     5	     6	      7
VALID_COMMANDS = ["Register", "UnRegister", "TakeOff", "Land", "UP", "DOWN", "RIGHT", "LEFT"] # Add new commands only at the end!!

class CrazyFlieObject(object):
	_cf = None
	_listener = None
	_name = None
	_pos = [-1,-1]
	_status = None
	def __init__(self, name):
		self._name = name
		#self._pos = [x,y]
		self._status = "OFF"
		self._listener = tf.TransformListener()
		self._cf = crazyflie.Crazyflie(name, name)
		self._cf.setParam("commander/enHighLevel", 1)
	def checkPosition():
		if self._status != "UP":
			return
		_real_pos,rot = self._listener.lookupTransform("/world", "/{}".format(self._name), rospy.Time(0))
		if _real_pos[2] < 0.1:
			print "Drone height too low, Aborting..."
			self._status = "OFF"
	def getStatus(self):
		return self._status
	def takeOff(self):
		self._cf.takeoff(targetHeight=FLIGHT_HEIGHT, duration=2)
		time.sleep(2)
		self._status = "UP"
	def land(self, landing_duration = 1.5):
		self._cf.land(targetHeight=0.0, duration=landing_duration)
		time.sleep(landing_duration)
		try:
			self._cf.stop()
		except Exception as e:
			print "Failed to stop CrazyFlie"
			print e
		self._status = "OFF"
	def doMovement(self):
		target_pos = cell2pos(self._pos)
		self._cf.goTo(goal=[target_pos[0],target_pos[1],FLIGHT_HEIGHT], yaw=0.0, duration=2, relative=False)
		time.sleep(2)
		_real_pos,rot = self._listener.lookupTransform("/world", "/{}".format(self._name), rospy.Time(0))
		print "{} is at ({:.2f},{:.2f},{:.2f}), Should be ({:.2f},{:.2f},{:.2f})".format(self._name,_real_pos[0],_real_pos[1],_real_pos[2],target_pos[0],target_pos[1],FLIGHT_HEIGHT)
	def goTo(self, x, y):
		self._pos = [x,y]
		self.doMovement()
	def move(self, direction):
		if direction == "UP":
			self._pos[1] -= 1 # Decrease the value in Y axis
		elif direction == "DOWN":
			self._pos[1] += 1 # Increase the value in Y axis
		elif direction == "RIGHT":
			self._pos[0] -= 1 # Decrease the value in X axis
		elif direction == "LEFT":
			self._pos[0] += 1 # Increase the value in X axis
		self.doMovement()
	def getPos(self):
		return self._pos

def cell2pos(cell):
	ret_x = round(WORLD_ORIGIN["X"] + (cell[0]*WORLD_STEPS["X"]),2)
	ret_y = round(WORLD_ORIGIN["Y"] + (cell[1]*WORLD_STEPS["Y"]),2)
	return [ret_x,ret_y]

def handleSocket():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1) # Accept only one connection at a time
	while True: # Keep waiting for connection
		print "Waiting for incoming connection"
		try:
			conn, addr = s.accept()
		except KeyboardInterrupt:
			print "Keyboard Interrupt"
			break
		print "#"*40 + "\nNew connection from: {}:{}".format(addr[0],addr[1])
		while 1:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				if KNOWN_CRAZYFLIES: # There are still registered drones
					for cf_name,cf_object in KNOWN_CRAZYFLIES.iteritems():
						if cf_object.getStatus() == "UP":
							print "Warning, Emergency landing for {}".format(cf_name)
							cf_object.land() # WTF
						print "Warning, Remove registered drone '{}'".format(cf_name)
						del cf_object
				break
			if 1 <= data.count("$"):
				loop_ret = "INVALID"
				loop_command = data.split("$")
				if loop_command[1] == VALID_COMMANDS[0]: # Register
					if loop_command[0] not in KNOWN_CRAZYFLIES:
						try:
							print "Add new drone: {}".format(loop_command[0])
							KNOWN_CRAZYFLIES[loop_command[0]] = CrazyFlieObject(loop_command[0]) # Drone is new
							loop_ret = "OK"
						except Exception as e:
							print "Failed to create CrazyFlie"
							print e
				elif loop_command[1] == VALID_COMMANDS[1]: # UnRegister
					if (loop_command[0] in KNOWN_CRAZYFLIES) and (KNOWN_CRAZYFLIES[loop_command[0]].getStatus() == "OFF"):
						print "Remove drone: {}".format(loop_command[0])
						del KNOWN_CRAZYFLIES[loop_command[0]] # Drone is known and down
						loop_ret = "OK"
				elif loop_command[1] == VALID_COMMANDS[2]: # TakeOff
					if len(loop_command) == 4:
						if (loop_command[0] in KNOWN_CRAZYFLIES) and (KNOWN_CRAZYFLIES[loop_command[0]].getStatus() == "OFF"):
							print "Takeoff {} and go to ({},{})".format(loop_command[0],loop_command[2],loop_command[3])
							KNOWN_CRAZYFLIES[loop_command[0]].takeOff() # Drone is known and down
							KNOWN_CRAZYFLIES[loop_command[0]].goTo(int(loop_command[2]),int(loop_command[3]))
							loop_ret = "OK"
				elif loop_command[1] == VALID_COMMANDS[3]: # Land
					if (loop_command[0] in KNOWN_CRAZYFLIES) and (KNOWN_CRAZYFLIES[loop_command[0]].getStatus() == "UP"):
						print "Land {}".format(loop_command[0])
						KNOWN_CRAZYFLIES[loop_command[0]].land() # Drone is known and up
						loop_ret = "OK"
				elif loop_command[1] in VALID_DIRECTIONS: # "UP", "DOWN", "RIGHT", "LEFT"
					if (loop_command[0] in KNOWN_CRAZYFLIES) and (KNOWN_CRAZYFLIES[loop_command[0]].getStatus() == "UP"):
						print "{} moved {}".format(loop_command[0],loop_command[1]),
						KNOWN_CRAZYFLIES[loop_command[0]].move(loop_command[1])
						cur_cell = KNOWN_CRAZYFLIES[loop_command[0]].getPos()
						print ", location ({},{})".format(cur_cell[0],cur_cell[1])
						loop_ret = "OK"
				else:
					print "Received invalid command: {} => {}".format(loop_command[0],loop_command[1])
				conn.send(loop_ret)
			else:
				print "Invalid data received: '{}'".format(data)
				conn.send("FORMAT")
		print "Closing connection with {}:{}".format(addr[0],addr[1])
		conn.close()

def main():
	WORLD_STEPS["X"] = round(abs(WORLD_RANGE["X"][1]-WORLD_RANGE["X"][0])/WORLD_CELLS_COUNT["X"],2) # X
	WORLD_STEPS["Y"] = round(abs(WORLD_RANGE["Y"][1]-WORLD_RANGE["Y"][0])/WORLD_CELLS_COUNT["Y"],2) # Y
	WORLD_ORIGIN["X"] = min(WORLD_RANGE["X"][0],WORLD_RANGE["X"][1])
	WORLD_ORIGIN["Y"] = min(WORLD_RANGE["Y"][0],WORLD_RANGE["Y"][1])
	rospy.init_node('the_new_gofetch')
	handleSocket()

if __name__ == '__main__':
	main()
