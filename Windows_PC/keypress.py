#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

def key_handle():
	import termios
	import sys, tty
	def _getch():
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(fd)
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch
	return _getch()

def getchar():
	state = 1
	while 1:
		key = ord(key_handle())
		if (state == 1) or (key == 0):
			if key == 27:
				state = 2
			else:
				return [False,chr(key)]
		elif (state == 2) and (key == 91):
			state = 3
		else:
			if state == 3:
				if key == 65: # ESC + '[' + 'A'
					return [True,"UP"]
				elif key == 66: # ESC + '[' + 'B'
					return [True,"DOWN"]
				elif key == 67: # ESC + '[' + 'C'
					return [True,"RIGHT"]
				elif key == 68: # ESC + '[' + 'D'
					return [True,"LEFT"]
			return [False,""]

def main():
	key_type, key_value = getchar()
	if key_type:
		print "You ask the CrazyFlie to move: {}".format(key_value)
	elif len(key_value) == 1:
		key_ord = ord(key_value)
		if (key_ord == 0) or (key_ord == 3) or (key_ord == 81) or (key_ord == 113): # Null or Ctrl+C or 'Q' or 'q'
			print "You asked to exit"
		else:
			print "You pressed: {}".format(key_value)
	else:
		print "Invalid key pressed"

if __name__ == "__main__":
	main()

