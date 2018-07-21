#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,threading,time
import libCrazyGame as libCG # CrazyGame custom library
from oracle import MagicOracle # CrazyGame custom library

#############################################################################################################
##	Hard coded crazyflie drones names						## XXX XXX XXX XXX ##
########################################################################################## XXX XXX XXX XXX ##
CRAZYFLIES_P1 = {"tools": ["crazyflie1", "crazyflie2"], "target": "rigidobject1"}	## XXX XXX XXX XXX ##
CRAZYFLIES_P2 = {"tools": ["crazyflie3", "crazyflie4"], "target": "rigidobject2"}	## XXX XXX XXX XXX ##
#############################################################################################################

class ElapsedTime(threading.Thread):
	_work = True
	_start_time = None
	def __init__(self, args=(), kwargs=None, verbose=None):
		threading.Thread.__init__(self)
		self.args = args
		self.kwargs = kwargs
	def stop(self):
		self._work = False
	def run(self):
		self._start_time = time.time()
		while self._work:
			diff = time.time()-self._start_time
			libCG.updateInfo(libCG.INFO_ELAPSED,"{:.0f}".format(diff)) # Update the requested value at the CLI info box
			time.sleep(1-(diff%1))

class CFPlayer(object):
	_player_Type = libCG.HUMAN_PLAYER
	_tools = None
	_target = None
	def __init__(self, player_Type, tools_names):
		if player_Type == libCG.COMPUTER_PLAYER: # We support only two types of players
			self._player_Type = libCG.COMPUTER_PLAYER
		self._tools = tools_names["tools"]
		self._target = tools_names["target"]
	def getMove(self, current_board):
		tool_to_move = 0 # TODO Let the user the option to choose
		if self._player_Type == libCG.HUMAN_PLAYER:
			while True: # Keep asking for valid moves
				key_type, key_value = libCG.getchar() # Wrapper for "key_handle()" in order to support the Up/Down/Left/Right keys
				if key_type:
					return [self._tools[tool_to_move],key_value] # key_value = "UP"/"DOWN"/"LEFT"/"RIGHT"
				elif len(key_value) == 1:
					key_ord = ord(key_value)
					if (key_ord == 0) or (key_ord == 3) or (key_ord == 81) or (key_ord == 113): # Null or Ctrl+C or 'Q' or 'q'
						libCG.printStatus("You asked to exit") # XXX DEBUG # Print status message (message length up to 130 chars)
						return ["None",None]
		else:
			# TODO The computer should check the data at "current_board"
			libCG.printStatus("Computer part will be added in the future") # XXX DEBUG # Print status message (message length up to 130 chars)
			return ["None",None]

def main():
	libCG.drawBoxs() # Print to the screen the frame of the CLI
	players_list = [CFPlayer(libCG.HUMAN_PLAYER,CRAZYFLIES_P1), CFPlayer(libCG.HUMAN_PLAYER,CRAZYFLIES_P2)]
	# Init the crazyflies
	if (libCG.BOARD_SIZE_X <= 6) or (libCG.BOARD_SIZE_Y <= 6): # Verify the board size
		libCG.printStatus("Game board is too small ({}X{})".format(libCG.BOARD_SIZE_X,libCG.BOARD_SIZE_Y)) # XXX DEBUG # Print status message (message length up to 130 chars)
		return
	oracle = MagicOracle([libCG.BOARD_SIZE_X,libCG.BOARD_SIZE_Y],CRAZYFLIES_P1,CRAZYFLIES_P2) # Create new thread
	oracle.daemon = True
	board = oracle.initGame()
	libCG.drawPiece(board)
	# Start the game
	current_player = 0
	turns_count = 0
	libCG.updateInfo(libCG.INFO_STATUS,"Running") # Update the requested value at the CLI info box
	libCG.printStatus("Press Ctrl+C or 'q' to exit") # XXX DEBUG # Print status message (message length up to 130 chars)
	thrd = ElapsedTime() # Create new thread
	thrd.daemon = True
	thrd.start() # Start the timer
	game_is_on = True
	while game_is_on: # The game will never end (unless some error will occur)
		libCG.changePlayerVisual(current_player+1) # Update the CLI when the current user has changed
		libCG.updateInfo(libCG.INFO_TURNS,str(turns_count)) # Update the requested value at the CLI info box
		if 1000 < turns_count: # make it a tie
			libCG.printStatus("Game ended after 1,000 moves without a winner") # XXX DEBUG # Print status message (message length up to 130 chars)
			break
		exit_game = False
		while True:
			loop_tool,loop_move = players_list[current_player].getMove(board)
			if not loop_move: # The user asked to exit
				exit_game = True
				break
			move_is_valid,game_is_on,old_pos = oracle.moveCF(current_player,loop_tool,loop_move)
			if move_is_valid or not game_is_on: # Move is valid
				break
		if exit_game:
			break
		if game_is_on:
			libCG.printStatus("Player {} move {} {}, Now it's the turn of player {}".format(current_player+1,loop_tool,loop_move,2-current_player)) # XXX DEBUG # Print status message (message length up to 130 chars)
		else: # Player reach the target
			libCG.printStatus("We have a winner") # XXX DEBUG # Print status message (message length up to 130 chars)
		libCG.drawPiece(board,old_pos)
		current_player = 1-current_player # Switch user
		turns_count += 1
	thrd.stop() # Stop the timer
	libCG.updateInfo(libCG.INFO_STATUS,"Ended") # Update the requested value at the CLI info box
	os.system('clear')

if __name__ == '__main__':
	main()

