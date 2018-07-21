#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
#import crazyflie, rospy, tf, uav_trajectory # TODO Uncomment
#import numpy as np # TODO Uncomment

# Those variables are here so you will be able to understand my code more easily :)
VALID_MOVE = True
INVALID_MOVE = False
GAME_IS_ON = True
GAME_OVER = False

class MagicOracle(threading.Thread):
	_board = {}
	_cf_name_mapping = {}
	_board_size = [0,0]
	_cf_per_player = 0
#	_listeners = None # TODO Uncomment
	_player_1_tools = {"tools": ["None"], "target": "None"}
	_player_2_tools = {"tools": ["None"], "target": "None"}
	def __init__(self, board_size, player_1_tools, player_2_tools, *args):
		threading.Thread.__init__(self)
		self.args = args
		self._board_size = board_size
		# Init "_cf_per_player"
		p1_count = len(player_1_tools["tools"])
		p2_count = len(player_2_tools["tools"])
		if (2 <= p1_count) and (2 <= p2_count): # Both player asked for two drones
			self._cf_per_player = 2
		elif (1 <= p1_count) and (1 <= p2_count): # Both players can support at least one drone
			self._cf_per_player = 1
		#
		self._player_1_tools = player_1_tools
		self._player_2_tools = player_2_tools
		#
#		self._name = name
#		self._listener = tf.TransformListener()
#		self._cf = crazyflie.Crazyflie(name, name)
#		self._cf.setParam("commander/enHighLevel", 1)
#		self._listeners = tf.TransformListener() # TODO Uncomment
		
#	def getPosition(self, crazyflie_name):
#		real_pos,rot = self._listeners.lookupTransform("/world", "/{}".format(crazyflie_name), rospy.Time(0))
#		return real_pos
#	def takeoff(self,x=0,y=0,z=0.5):
#		z_time = round(abs(self._real_pos[2]-z),2) * 4.0 # How many sec the drone will need in order to be at the requested height
#		xy_distance = round(math.sqrt(pow(self._real_pos[0]-x, 2) + pow(self._real_pos[1]-y, 2)),2)
#		xy_time = xy_distance * 4.0
#		print "Takeoff (This will take {} seconds)".format(z_time)
#		self._cf.takeoff(targetHeight=z, duration=z_time)
#		time.sleep(z_time)
#		print "Going to the start location (This will take {} seconds)".format(xy_time)
#		self._cf.goTo(goal=[x,y,z], yaw=0.0, duration=xy_time, relative=False)
#		time.sleep(xy_time)
#		self.updateLocation()
#		print "At ({:.2f},{:.2f},{:.2f}), Should be ({:.2f},{:.2f},{:.2f})".format(self._real_pos[0],self._real_pos[1],self._real_pos[2],x,y,z)
#		if self._real_pos[2] < 0.1:
#			print "Drone height too low, Aborting..."
#			return
#	def land(self,landing_duration = 1.5):
#		self._cf.land(targetHeight=0.0, duration=landing_duration)
#		time.sleep(landing_duration)
#		self._cf.stop()
	def initGame(self):
		# TODO take the drones takeoff and set them at position
		self._board = {}
		if self._cf_per_player == 1:
			# Player 1
			self._board["1"] = [0,1+(self._board_size[1]//2)] # First tool
			self._cf_name_mapping[self._player_1_tools["tools"][0]] = "1"
#			tmp_cf_name = self._player_1_tools["tools"][0]
#			# TODO Make "tmp_cf_name" get stable at his initial position
			# Player 2
			self._board["A"] = [self._board_size[0],1+(self._board_size[1]//2)] # First tool
			self._cf_name_mapping[self._player_2_tools["tools"][0]] = "A"
#			tmp_cf_name = self._player_2_tools["tools"][0]
#			# TODO Make "tmp_cf_name" get stable at his initial position
		elif self._cf_per_player == 2:
			# Player 1
			self._board["1"] = [0,2] # First tool
			self._board["2"] = [0,self._board_size[1]-3] # Second tool
			self._cf_name_mapping[self._player_1_tools["tools"][0]] = "1"
			self._cf_name_mapping[self._player_1_tools["tools"][1]] = "2"
#			tmp_cf_name_0 = self._player_1_tools["tools"][0]
#			tmp_cf_name_1 = self._player_1_tools["tools"][1]
#			# TODO Make "tmp_cf_name_0" get stable at his initial position
#			# TODO Make "tmp_cf_name_1" get stable at his initial position
			# Player 2
			self._board["A"] = [self._board_size[0]-1,2] # First tool
			self._board["B"] = [self._board_size[0]-1,self._board_size[1]-3] # Second tool
			self._cf_name_mapping[self._player_2_tools["tools"][0]] = "A"
			self._cf_name_mapping[self._player_2_tools["tools"][1]] = "B"
#			tmp_cf_name_0 = self._player_2_tools["tools"][0]
#			tmp_cf_name_1 = self._player_2_tools["tools"][1]
#			# TODO Make "tmp_cf_name_0" get stable at his initial position
#			# TODO Make "tmp_cf_name_1" get stable at his initial position
		else: # Bad input
			return {}
		self._board["3"] = [self._board_size[0]-1,self._board_size[1]//2] # Player 1 targed
		self._board["C"] = [0,self._board_size[1]//2] # Player 2 targed
		self._cf_name_mapping[self._player_1_tools["target"]] = "3"
		self._cf_name_mapping[self._player_2_tools["target"]] = "C"
		return self._board
	def checkEmpty(self,cell):
		for piece,position in self._board.iteritems():
			if (position[0] == cell[0]) and (position[1] == cell[1]):
				return piece
		return ""
	def moveCF(self, player_number, cf_name, move_direction):
		cf_short_name = self._cf_name_mapping[cf_name]
		cf_sbackup_pos = [self._board[cf_short_name][0],self._board[cf_short_name][1]]
		game_is_on = GAME_IS_ON
		invalid_move = INVALID_MOVE
		new_pos_x = self._board[cf_short_name][0]
		new_pos_y = self._board[cf_short_name][1]
		if (move_direction == "UP") and (self._board[cf_short_name][1] < self._board_size[1]-1): # Player asked to move "UP" and it is inside the game borders
			target_piece = self.checkEmpty([self._board[cf_short_name][0],self._board[cf_short_name][1]+1])
			if target_piece == "": # Next cell is empty:
				invalid_move = VALID_MOVE
				new_pos_y = self._board[cf_short_name][1]+1
			if ((player_number+1 == 1) and (target_piece == self._cf_name_mapping[self._player_1_tools["target"]])) or ((player_number+1 == 2) and (target_piece == self._cf_name_mapping[self._player_2_tools["target"]])): # Player is going to win
				game_is_on = GAME_OVER
		elif (move_direction == "DOWN") and (0 < self._board[cf_short_name][1]): # Player asked to move "DOWN" and it is inside the game borders
			target_piece = self.checkEmpty([self._board[cf_short_name][0],self._board[cf_short_name][1]-1])
			if target_piece == "": # Next cell is empty:
				invalid_move = VALID_MOVE
				new_pos_y = self._board[cf_short_name][1]-1
			if ((player_number+1 == 1) and (target_piece == self._cf_name_mapping[self._player_1_tools["target"]])) or ((player_number+1 == 2) and (target_piece == self._cf_name_mapping[self._player_2_tools["target"]])): # Player is going to win
				game_is_on = GAME_OVER
		elif (move_direction == "RIGHT") and (0 < self._board[cf_short_name][0]): # Player asked to move "RIGHT" and it is inside the game borders
			target_piece = self.checkEmpty([self._board[cf_short_name][0]-1,self._board[cf_short_name][1]])
			if target_piece == "": # Next cell is empty:
				invalid_move = VALID_MOVE
				new_pos_x = self._board[cf_short_name][0]-1
			if ((player_number+1 == 1) and (target_piece == self._cf_name_mapping[self._player_1_tools["target"]])) or ((player_number+1 == 2) and (target_piece == self._cf_name_mapping[self._player_2_tools["target"]])): # Player is going to win
				game_is_on = GAME_OVER
		elif (move_direction == "LEFT") and (self._board[cf_short_name][0] < self._board_size[0]-1): # Player asked to move "LEFT" and it is inside the game borders
			target_piece = self.checkEmpty([self._board[cf_short_name][0]+1,self._board[cf_short_name][1]])
			if target_piece == "": # Next cell is empty:
				invalid_move = VALID_MOVE
				new_pos_x = self._board[cf_short_name][0]+1
			if ((player_number+1 == 1) and (target_piece == self._cf_name_mapping[self._player_1_tools["target"]])) or ((player_number+1 == 2) and (target_piece == self._cf_name_mapping[self._player_2_tools["target"]])): # Player is going to win
				game_is_on = GAME_OVER
		if invalid_move == VALID_MOVE:
			self._board[cf_short_name][0] = new_pos_x
			self._board[cf_short_name][1] = new_pos_y
		return [invalid_move,game_is_on,cf_sbackup_pos]

