import pygame
from pygame.locals import *
import numpy as np

PLAYER = 1  # 1 for HUMAN, 0 for MACHINE

WINDOW_WIDTH = 1000  # width of the program's window, in pixels
WINDOW_HEIGHT = 800  # height in pixels
BOARD_WIDTH = 550  # width of the board's visualization
BOARD_HEIGHT = 550  # height of the board's visualization
SAFE_ZONE = 15.0  # minimal distance between 2 drones

# colors: R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BLUE  = (0, 50, 255)
BROWN = (174, 94, 0)
RED   = (255, 0, 0)


class Board:

    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def __init__(self, width, height):
        # Creates a brand new, empty board data structure
        self.turns = 0
        self.time = 0
        self.players = None
        self.width, self.height = width, height
        self.x_margin = int(int(WINDOW_WIDTH / 10))
        self.y_margin = int(int(WINDOW_HEIGHT / 10))
        self.grid_line_color = BLUE
        return

    def add_players(self, player1, player2):
        self.players = player1 + player2

    def draw_text(self, text, x, y, color):
        large_text = pygame.font.Font('freesansbold.ttf', 30)
        text_surf = large_text.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        self.DISPLAYSURF.blit(text_surf, text_rect)

    def convert_xy(self, x, y):
        """ convert real world coordinates to board's coordinates
            where (0,0) is top-right corner of real-world game field
            positive X is directed right and positive Y is directed down"""
        x_unit = BOARD_WIDTH/self.width
        y_unit = BOARD_HEIGHT/self.height
        new_x = self.x_margin + BOARD_WIDTH - (x * x_unit)
        new_y = self.y_margin + (y * y_unit)
        return new_x, new_y

    def draw_board(self):
        pygame.init()
        pygame.display.set_caption('Crazy Hell Game')

        # the color of the board is blue on the human player's turn, and red on the computer's turn
        self.grid_line_color = BLUE if PLAYER else RED

        # Draw high board line
        pygame.draw.line(self.DISPLAYSURF, self.grid_line_color, (self.x_margin, self.y_margin),
                         (self.x_margin + BOARD_WIDTH, self.y_margin))
        # Draw low board line
        pygame.draw.line(self.DISPLAYSURF, self.grid_line_color, (self.x_margin, self.y_margin + BOARD_HEIGHT),
                         (self.x_margin + BOARD_WIDTH, self.y_margin + BOARD_HEIGHT))
        # Draw left board line
        pygame.draw.line(self.DISPLAYSURF, self.grid_line_color, (self.x_margin, self.y_margin),
                         (self.x_margin, self.y_margin + BOARD_HEIGHT))
        # Draw right board line
        pygame.draw.line(self.DISPLAYSURF, self.grid_line_color, (self.x_margin + BOARD_WIDTH, self.y_margin),
                         (self.x_margin + BOARD_WIDTH, self.y_margin + BOARD_HEIGHT))

        # Draw players' drones
        for player in self.players:
            if player.type:  # if human
                pygame.draw.circle(self.DISPLAYSURF, GREEN, (int(round(player.pos[0])), int(round(player.pos[1]))), 3)
            else:
                pygame.draw.circle(self.DISPLAYSURF, WHITE, (int(round(player.pos[0])), int(round(player.pos[1]))), 3)

        # Draw Game Info
        self.draw_text("Turns:  " + str(self.turns), WINDOW_WIDTH - self.x_margin, self.y_margin, BROWN)
        self.draw_text("Time:  " + str(self.time), WINDOW_WIDTH - self.x_margin, 2*self.y_margin, BROWN)

    def move_player(self, player, direction, x=0, y=0):
        """ moves player on the board while updating player's info
            unless move isn't valid then an error is printed to the user
            @return: 0 if not a valid move, 1 else """
        if player.type:  # for the human player
            if direction == "UP":
                new_pos = [player.pos[0], player.pos[1] + 1]
            elif direction == "DOWN":
                new_pos = [player.pos[0], player.pos[1] - 1]
            elif direction == "LEFT":
                new_pos = [player.pos[0] + 1, player.pos[1]]
            elif direction == "RIGHT":
                new_pos = [player.pos[0] - 1, player.pos[1]]
            else:
                print("ERROR: Wrong direction input")
                return False
            # validate the move
            if self.is_valid_move(player.name, new_pos):
                player.move(new_pos)
                return True
            else:
                return False

        else:  # for the machine player
            if self.is_valid_move(player.name, [x, y]):
                player.move([x, y])
                return True
            else:
                return False

    def is_valid_move(self, name, new_pos):
        if 0 <= new_pos[0] < self.width and 0 <= new_pos[1] < self.height:
            for player in self.players:
                if name != player.name:
                    if np.linalg.norm([player.pos[i]-new_pos[i] for i in range(2)]) <= SAFE_ZONE:
                        return False
            return True
        return False


class Player:

    def __init__(self, player_type, name, x, y):
        self.type = player_type  # 1 for human, 0 for computer
        self.name = name  # the name of the specific drone - rigid1 for example
        self.pos = [x, y]  # the player's position on the board
        return

    def move(self, new_pos):
        self.pos = new_pos
        return

    def get_move(self):
        """ if it's the human player - get direction from user
            otherwise - ask the computer to generate a move using
            the algorithm """
        pass

