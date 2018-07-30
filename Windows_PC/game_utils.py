import sys
import pygame
import numpy as np

from pygame.locals import *

#         R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BLUE = (0, 50, 255)
BROWN = (174, 94, 0)


class Board:

    board = []
    turns = 0
    time = 0
    window_width = 1000  # width of the program's window, in pixels
    window_height = 800  # height in pixels
    space_size = 50  # width & height of each space on the board, in pixels
    board_width = 8  # how many columns of spaces on the game board
    board_height = 8  # how many rows of spaces on the game board
    empty = ""  # an arbitrary but unique value
    x_margin = int(int((window_width - (board_width * space_size)) / 2)/3)
    y_margin = int((window_height - (board_height * space_size)) / 2)

    DISPLAYSURF = pygame.display.set_mode((window_width, window_height))
    TEXTBGCOLOR1 = BLUE
    TEXTBGCOLOR2 = GREEN
    grid_line_color = BLUE
    TEXTCOLOR = WHITE

    def __init__(self):
        # Creates a brand new, empty board data structure.
        for i in range(self.board_width):
            self.board.append([self.empty] * self.board_height)
        return

    def add_players(self, player1, player2):
        self.board[player1["rigid1"][0]][player1["rigid1"][1]] = "A"
        self.board[player1["rigid2"][0]][player1["rigid2"][1]] = "B"
        self.board[player2["rigid3"][0]][player2["rigid3"][1]] = "a"
        self.board[player2["rigid4"][0]][player2["rigid4"][1]] = "b"

    def draw_item(self, text, x, y, color):
        large_text = pygame.font.Font('freesansbold.ttf', 30)
        text_surf = large_text.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = ((self.space_size / 2) + self.x_margin + x * self.space_size, (self.space_size / 2) +
                           self.y_margin + y * self.space_size)
        self.DISPLAYSURF.blit(text_surf, text_rect)

    def draw_text(self, text, x, y, color):
        large_text = pygame.font.Font('freesansbold.ttf', 30)
        text_surf = large_text.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        self.DISPLAYSURF.blit(text_surf, text_rect)

    def draw_board(self):
        pygame.init()
        pygame.display.set_caption('Crazy Hell Game')
        font = pygame.font.Font('freesansbold.ttf', 16)
        bigfont = pygame.font.Font('freesansbold.ttf', 32)

        # Draw grid lines of the board.
        for x in range(self.board_width + 1):
            # Draw the horizontal lines.
            start_x = (x * self.space_size) + self.x_margin
            start_y = self.y_margin
            end_x = (x * self.space_size) + self.x_margin
            end_y = self.y_margin + (self.board_height * self.space_size)
            pygame.draw.line(self.DISPLAYSURF, self.grid_line_color, (start_x, start_y), (end_x, end_y))
        for y in range(self.board_height + 1):
            # Draw the vertical lines.
            start_x = self.x_margin
            start_y = (y * self.space_size) + self.y_margin
            end_x = self.x_margin + (self.board_width * self.space_size)
            end_y = (y * self.space_size) + self.y_margin
            pygame.draw.line(self.DISPLAYSURF, self.grid_line_color, (start_x, start_y), (end_x, end_y))

        # Add starting pieces to the center
        for i in range(self.board_width):
            for j in range(self.board_height):
                if(self.board[i][j] != self.empty):
                    if self.board[i][j].isupper():
                        self.draw_item(self.board[i][j], i, j, WHITE)
                    else:
                        self.draw_item(self.board[i][j], i, j, GREEN)

        # Draw Game Info
        self.draw_text("Turns:  " + str(self.turns), self.window_width * 0.75, self.y_margin, BROWN)
        self.draw_text("Time:  " + str(self.time), self.window_width * 0.75, 2*self.y_margin, BROWN)
