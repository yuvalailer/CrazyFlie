#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading, time
import lib # Our lib

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
			lib.updateInfo(lib.INFO_ELAPSED,"{:.0f}".format(diff)) # Update the requested value at the CLI info box
			time.sleep(1-(diff%1))

class CFPlayer(object):
	_player_Type = lib.HUMAN_PLAYER
	def __init__(self, player_Type):
		if player_Type == lib.COMPUTER_PLAYER: # We support only two types of players
			self._player_Type = lib.COMPUTER_PLAYER
	def getMove(self):
		if self._player_Type == lib.HUMAN_PLAYER:
			while True: # Keep asking for valid moves
				key_type, key_value = lib.getchar() # Wrapper for "key_handle()" in order to support the Up/Down/Left/Right keys
				if key_type:
					return key_value # key_value = "UP"/"DOWN"/"LEFT"/"RIGHT"
				elif len(key_value) == 1:
					key_ord = ord(key_value)
					if (key_ord == 0) or (key_ord == 3) or (key_ord == 81) or (key_ord == 113): # Null or Ctrl+C or 'Q' or 'q'
						lib.printStatus("You asked to exit") # TODO DEBUG # Print status message (message length up to 130 chars)
						return None
		else:
			lib.printStatus("Computer part will be added in the future") # TODO DEBUG # Print status message (message length up to 130 chars)
			return None

def main():
	lib.drawBoxs() # Print to the screen the frame of the CLI
	players_list = [CFPlayer(lib.HUMAN_PLAYER), CFPlayer(lib.HUMAN_PLAYER)]
	current_player = 0
	turns_count = 0
	lib.updateInfo(lib.INFO_STATUS,"Running") # Update the requested value at the CLI info box
	lib.printStatus("Press Ctrl+C or 'q' to exit") # TODO DEBUG # Print status message (message length up to 130 chars)
	thrd = ElapsedTime() # Create new thread
	thrd.daemon = True
	thrd.start() # Start the timer
	while True: # The game will never end (unless some error will occur)
		lib.changePlayerVisual(current_player+1) # Update the CLI when the current user has changed
		lib.updateInfo(lib.INFO_TURNS,str(turns_count)) # Update the requested value at the CLI info box
		loop_move = players_list[current_player].getMove()
		if not loop_move:
			break
		lib.printStatus("Player {} move {}, Now it's the turn of player {}".format(current_player+1,loop_move,2-current_player)) # TODO DEBUG # Print status message (message length up to 130 chars)
		current_player = 1-current_player # Switch user
		turns_count += 1
	thrd.stop() # Stop the timer
	lib.updateInfo(lib.INFO_STATUS,"Ended") # Update the requested value at the CLI info box

if __name__ == '__main__':
	main()
