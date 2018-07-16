#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys,time

BOARD_SIZE_X = 10
BOARD_SIZE_Y = 10

def drawBoxs():
	os.system('clear')
	# Title
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 2, "Welcome to the CrazyGame"))
	# Pring game board
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (3, 2, "╔{}═╗".format("═╤"*(BOARD_SIZE_X-1))))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (4, 2, "║{} ║".format(" │"*(BOARD_SIZE_X-1))))
	for indx in range(BOARD_SIZE_Y-1):
		sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (5+2*indx, 2, "╟{}─╢".format("─┼"*(BOARD_SIZE_X-1))))
		sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (6+2*indx, 2, "║{} ║".format(" │"*(BOARD_SIZE_X-1))))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (3+2*BOARD_SIZE_Y, 2, "╚{}═╝".format("═╧"*(BOARD_SIZE_X-1))))
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
	#
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (17, 4+2*BOARD_SIZE_X, "  Player 2   CrazyFlie: A  "))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (18, 4+2*BOARD_SIZE_X, "             CrazyFlie: B  "))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (19, 4+2*BOARD_SIZE_X, "             Targets:   C&D"))
	# Flush
	sys.stdout.flush()

def changePlayerVisual(current_player):
	if current_player == 1:
		p1_start = 9
		p2_start = 15
	else:
		p1_start = 15
		p2_start = 9
	# Bold the current player
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+1, 4+2*BOARD_SIZE_X, "█▀▀▀▀▀▀▀▀▀▀█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+2, 4+2*BOARD_SIZE_X, "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+2, 4+2*BOARD_SIZE_X+len(" Player X ")+1, "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+2, 4+2*BOARD_SIZE_X+len(" Player X █ CrazyFlie: X  "), "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+3, 4+2*BOARD_SIZE_X, "█ Current  █"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+3, 4+2*BOARD_SIZE_X+len(" Current  █ CrazyFlie: X  "), "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+4, 4+2*BOARD_SIZE_X, "█ Player   █"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+4, 4+2*BOARD_SIZE_X+len(" Player   █ Targets:   X&X"), "█"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p2_start+5, 4+2*BOARD_SIZE_X, "█▄▄▄▄▄▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█"))
	# Unbold the other player
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+1, 4+2*BOARD_SIZE_X, "╭──────────┬────────────────╮"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+2, 4+2*BOARD_SIZE_X, "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+2, 4+2*BOARD_SIZE_X+len(" Player X ")+1, "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+2, 4+2*BOARD_SIZE_X+len(" Player X │ CrazyFlie: X  "), "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+3, 4+2*BOARD_SIZE_X, "│          │"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+3, 4+2*BOARD_SIZE_X+len("          │ CrazyFlie: X  "), "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+4, 4+2*BOARD_SIZE_X, "│          │"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+4, 4+2*BOARD_SIZE_X+len("          │ Targets:   X&X"), "│"))
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (p1_start+5, 4+2*BOARD_SIZE_X, "╰──────────┴────────────────╯"))
	sys.stdout.flush()

def main():
	drawBoxs()
	changePlayerVisual(2)
	for indx in range(5):
		time.sleep(1)
		changePlayerVisual(1+(indx%2))

if __name__ == '__main__':
	main()
