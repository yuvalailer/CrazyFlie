#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys,time

BOARD_SIZE_X = 10
BOARD_SIZE_Y = 10

HUMAN_PLAYER = 0
COMPUTER_PLAYER = 1

INFO_STATUS = 0
INFO_TURNS = 1
INFO_ELAPSED = 2

#
# def drawBoxs()
#	Print to the screen the frame of the CLI
#
# def changePlayerVisual(current_player)
#	Update the CLI when the current user has changed
#
# def printStatus(status)
#	Print status message (message length up to 130 chars)
#
# def updateInfo(info_type, new_value)
#	Update the requested value at the CLI info box
#
# def key_handle()
#	Get one char from the keyboard
#
# def getchar()
#	Wrapper for "key_handle()" in order to support the Up/Down/Left/Right keys
#

def drawBoxs(): # Print to the screen the frame of the CLI
	os.system('clear')
	# Title
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 1, 2, "Welcome to the CrazyGame"))
	# Pring game board
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 3, 2, "╔{}═╗".format("═╤"*(BOARD_SIZE_X-1))))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 4, 2, "║{} ║".format(" │"*(BOARD_SIZE_X-1))))
	for indx in range(BOARD_SIZE_Y-1):
		sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 5+2*indx, 2, "╟{}─╢".format("─┼"*(BOARD_SIZE_X-1))))
		sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 6+2*indx, 2, "║{} ║".format(" │"*(BOARD_SIZE_X-1))))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 3+2*BOARD_SIZE_Y, 2, "╚{}═╝".format("═╧"*(BOARD_SIZE_X-1))))
	# Game status
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 4, 4+2*BOARD_SIZE_X, "┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 5, 4+2*BOARD_SIZE_X, "┃ Game status  ┃               ┃"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 6, 4+2*BOARD_SIZE_X, "┃ Total turns  ┃               ┃"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 7, 4+2*BOARD_SIZE_X, "┃ Time elapsed ┃               ┃"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 8, 4+2*BOARD_SIZE_X, "┗━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━┛"))
	# Player 1
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (11, 4+2*BOARD_SIZE_X, "  Player 1   CrazyFlie: 1  "))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (12, 4+2*BOARD_SIZE_X, "             CrazyFlie: 2  "))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (13, 4+2*BOARD_SIZE_X, "             Targets:   3&4"))
	# player 2
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (17, 4+2*BOARD_SIZE_X, "  Player 2   CrazyFlie: A  "))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (18, 4+2*BOARD_SIZE_X, "             CrazyFlie: B  "))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (19, 4+2*BOARD_SIZE_X, "             Targets:   C&D"))
	# Flush
	sys.stdout.flush()

def changePlayerVisual(current_player): # Update the CLI when the current user has changed
	if current_player == 1:
		bolded_start = 9
		regular_start = 15
	else:
		bolded_start = 15
		regular_start = 9
	# Bold the current player
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+1, 4+2*BOARD_SIZE_X, "█▀▀▀▀▀▀▀▀▀▀█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+2, 4+2*BOARD_SIZE_X, "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+2, 4+2*BOARD_SIZE_X+len(" Player X ")+1, "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+2, 4+2*BOARD_SIZE_X+len(" Player X █ CrazyFlie: X  "), "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+3, 4+2*BOARD_SIZE_X, "█ Current  █"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+3, 4+2*BOARD_SIZE_X+len(" Current  █ CrazyFlie: X  "), "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+4, 4+2*BOARD_SIZE_X, "█ Player   █"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+4, 4+2*BOARD_SIZE_X+len(" Player   █ Targets:   X&X"), "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (bolded_start+5, 4+2*BOARD_SIZE_X, "█▄▄▄▄▄▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█"))
	# Unbold the other player
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+1, 4+2*BOARD_SIZE_X, "╭──────────┬────────────────╮"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+2, 4+2*BOARD_SIZE_X, "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+2, 4+2*BOARD_SIZE_X+len(" Player X ")+1, "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+2, 4+2*BOARD_SIZE_X+len(" Player X │ CrazyFlie: X  "), "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+3, 4+2*BOARD_SIZE_X, "│          │"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+3, 4+2*BOARD_SIZE_X+len("          │ CrazyFlie: X  "), "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+4, 4+2*BOARD_SIZE_X, "│          │"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+4, 4+2*BOARD_SIZE_X+len("          │ Targets:   X&X"), "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (regular_start+5, 4+2*BOARD_SIZE_X, "╰──────────┴────────────────╯"))
	sys.stdout.flush()

def printStatus(status): # Print status message (message length up to 130 chars)
	if len(status) < 130:
		status += " "*(130-len(status))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 5+2*BOARD_SIZE_Y, 2, status[:130]))
	sys.stdout.flush()

def updateInfo(info_type, new_value): # Update the requested value at the CLI info box
	if (info_type == INFO_STATUS) or (info_type == INFO_TURNS) or (info_type == INFO_ELAPSED):
		if len(new_value) < 13:
			new_value += " "*(13-len(new_value))
		sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % ( 5+info_type,21+2*BOARD_SIZE_X, new_value[:13]))
	else:
		return
	sys.stdout.flush() # Don't flush for invalid calls

def key_handle(): # Get one char from the keyboard
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

def getchar(): # Wrapper for "key_handle()" in order to support the Up/Down/Left/Right keys
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

if __name__ == '__main__':
	print "Wrong usage"

