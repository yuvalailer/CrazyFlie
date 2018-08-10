import pygame
import numpy as np
import sys
from shapely.geometry import Point


WINDOW_WIDTH = 1000  # width of the program's window, in pixels
WINDOW_HEIGHT = 800  # height in pixels
BOARD_WIDTH = 550  # width of the board's visualization
BOARD_HEIGHT = 550  # height of the board's visualization
SAFE_ZONE = 1.0  # minimal distance between 2 drones

# colors: R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BLUE = (0, 50, 255)
BROWN = (174, 94, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
GREY = (105, 105, 105)


class Board:
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    def __init__(self, width, height):
        # Creates a brand new, empty board data structure
        self.turns = 1
        self.time = 0
        self.players = []  # players is a list of Players
        self.drones_set = set()  #  set of drones in game
        self.width, self.height = width, height  # real world width and height
        self.x_margin = int(int(WINDOW_WIDTH / 10))
        self.y_margin = int(int(WINDOW_HEIGHT / 10))
        self.x_unit = BOARD_WIDTH/self.width  # the relative movement unit on the board horizontally
        self.y_unit = BOARD_HEIGHT/self.height  # the relative movement unit on the board vertically
        self.turn_sign = Text("Turn:  1", BROWN)
        self.time_sign = Text("Time:  0", BROWN)
        self.msg = Text("It's your Turn!", GREEN)
        return

    def reset_time(self):
        self.time = pygame.time.get_ticks()

    def add_players(self, player1, player2):
        self.players = [player1, player2]

    def add_drones(self, drones):
        for drone in drones:
            self.drones_set.add(drone)

    def convert_xy(self, x, y):
        """
        convert real world coordinates to board's coordinates
        where (0,0) is top-right corner of real-world game field
        positive x is directed right and positive y is directed down
        :param x: x coordinate of real-world perspective
        :param y: y coordinate of real-world perspective
        :return: new (x, y) according to game screen perspective
        """
        new_x = self.x_margin + BOARD_WIDTH - (x * self.x_unit)
        new_y = self.y_margin + (y * self.y_unit)
        return new_x, new_y

    def welcome(self):
        font = pygame.font.SysFont('arial', 80)
        surf = font.render("Welcome to The Crazy Game!!!", True, GOLD)
        rect = surf.get_rect()
        center = ((WINDOW_WIDTH-rect.width)//2, (WINDOW_HEIGHT-rect.height)//2)
        self.DISPLAYSURF.blit(surf, center)
        pygame.display.update()

    def finish(self):
        font = pygame.font.SysFont('arial', 80)
        surf = font.render("OMG!!!!!!!1 We Have A Winner!", True, GOLD)
        rect = surf.get_rect()
        center = ((WINDOW_WIDTH-rect.width)//2, (WINDOW_HEIGHT-rect.height)//2)
        self.DISPLAYSURF.blit(surf, center)
        pygame.display.update()

    def draw_board(self):
        self.DISPLAYSURF.fill(BLACK)  # clear board (critical to avoid overlapping)
        # the color of the board is green on the human player's turn, and white on the computer's turn
        grid_line_color = WHITE
        # Draw high board line
        pygame.draw.line(self.DISPLAYSURF, grid_line_color, (self.x_margin, self.y_margin),
                         (self.x_margin + BOARD_WIDTH, self.y_margin))
        # Draw low board line
        pygame.draw.line(self.DISPLAYSURF, grid_line_color, (self.x_margin, self.y_margin + BOARD_HEIGHT),
                         (self.x_margin + BOARD_WIDTH, self.y_margin + BOARD_HEIGHT))
        # Draw left board line
        pygame.draw.line(self.DISPLAYSURF, grid_line_color, (self.x_margin, self.y_margin),
                         (self.x_margin, self.y_margin + BOARD_HEIGHT))
        # Draw right board line
        pygame.draw.line(self.DISPLAYSURF, grid_line_color, (self.x_margin + BOARD_WIDTH, self.y_margin),
                         (self.x_margin + BOARD_WIDTH, self.y_margin + BOARD_HEIGHT))
        # Draw players' drones
        for player in self.players:
            for drone in player.drones:
                x_new, y_new = self.convert_xy(drone.pos.x, drone.pos.y) # Return tuple of x and y
                pygame.draw.circle(self.DISPLAYSURF, player.color, (int(round(x_new)), int(round(y_new))), 3)
        # Draw Game Info
        self.DISPLAYSURF.blit(self.turn_sign.surf, (WINDOW_WIDTH - 2*self.x_margin, self.y_margin))
        self.update_time(self.time_sign)  # set the new time
        self.DISPLAYSURF.blit(self.time_sign.surf, (WINDOW_WIDTH - 2*self.x_margin, 2*self.y_margin))  # paint new time
        center_x = (BOARD_WIDTH-self.msg.surf.get_rect().width)//2  # centralize msg respective to board
        self.DISPLAYSURF.blit(self.msg.surf, (self.x_margin + center_x, self.y_margin + BOARD_HEIGHT))
        pygame.display.update()  # repaint board

    def update_time(self, sign):
        """
        Updates the time in the time marker on the screen
        before painting in draw_board
        :param sign: the marker to use
        :return: void
        """
        sec_time = (pygame.time.get_ticks()-self.time)//1000  # time in seconds
        if sec_time < 60:
            sign.update("Time:  "+str(int(sec_time)), BROWN)
            return
        min_time = sec_time // 60  # minutes passed
        sec_time %= 60  # sec_time is now relative to the minute
        time_string = "%d:%02d" % (min_time, sec_time)
        sign.update("Time:  " + time_string, BROWN)
        return  # assuming we won't reach for an hour game...........

    def update_drone(self, color, old_radius, new_radius, pos):
        x_new, y_new = self.convert_xy(pos.x, pos.y)
        pygame.draw.circle(self.DISPLAYSURF, BLACK, (int(round(x_new)), int(round(y_new))), old_radius)
        pygame.draw.circle(self.DISPLAYSURF, color, (int(round(x_new)), int(round(y_new))), new_radius)
        pygame.display.update()

    def choose_drone(self, player):
        while True:
            for drone in player.drones:
                loop = True
                x_new, y_new = self.convert_xy(drone.pos.x, drone.pos.y)
                pygame.draw.circle(self.DISPLAYSURF, BLUE, (int(round(x_new)), int(round(y_new))), 4)
                pygame.display.update()
                while loop:
                    for event in pygame.event.get():
                        if not loop:
                            break
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                self.update_drone(player.color, 4, 3, drone.pos)
                                return drone
                            elif event.key == pygame.K_DOWN:
                                self.update_drone(player.color, 4, 3, drone.pos)
                                loop = False

    def move_drone(self, drone, direction):
        """
        moves drone on the board while updating drone's info
            unless move isn't valid then an error is printed to the user
        :param drone: the drone instance to be moved
        :param direction: String indicating the direction, or a Point(x, y)
        :return: 0 if not a valid move, 1 else
        """
        if drone.type == "human":  # for the human player
            if direction == "UP":
                new_pos = Point(drone.pos.x, drone.pos.y - 1)
            elif direction == "DOWN":
                new_pos = Point(drone.pos.x, drone.pos.y + 1)
            elif direction == "LEFT":
                new_pos = Point(drone.pos.x + 1, drone.pos.y)
            elif direction == "RIGHT":
                new_pos = Point(drone.pos.x - 1, drone.pos.y)
            else:
                print("ERROR: Wrong direction input: " + direction)
                return False
            print(new_pos.x, new_pos.y)
            # validate the move
            if self.is_valid_move(drone.name, new_pos):
                drone.move(new_pos)
                self.draw_board()  # NOTICE: this line happens even if the player doesn't press nothing
                # update turns:
                self.turns += 1
                self.turn_sign.update("Turn:  " + str(self.turns), BROWN)
                return True
            else:
                self.msg.update("Illegal move! Try again...", RED)  # indicate the player fo wrong move
                return False
        else:  # for the machine drone, now the direction is a Point(x, y)
            if self.is_valid_move(drone.name, direction):
                drone.move(direction)
                # update turns:
                self.turns += 1
                self.turn_sign.update("Turn:  " + str(self.turns), BROWN)
                return True
            else:
                return False

    def is_valid_move(self, name, new_pos):
        """
        checks if the new_pos is a valid point to move to
        :param name: name of Player instance (Player.name)
        :param new_pos: list - [x, y]
        :return: True if position is inside the board and with no obstacles, False otherwise
        """
        if self.is_in_board(new_pos):  # first check for boundaries
            for player in self.players:
                for drone in player.drones:
                    if name != drone.name:  # then check for collision
                        #if np.linalg.norm([np.abs(drone.pos.x-new_pos.x), np.abs(drone.pos.y-new_pos.y)]) <= SAFE_ZONE:
                        if drone.pos == new_pos:  # TODO: change back to euclidian distance
                            return False
            return True
        return False

    def is_in_board(self, new_pos):
        """
        helper function to is_valid_move
        :param new_pos: list [x, y]
        :return: True if new_pos is inside the board, False otherwise
        """
        return 0.0 <= new_pos.x <= self.width and 0.0 <= new_pos.y <= self.height


class Drone:
    """
    A class to represent a single entity of the game (drone)
    """
    def __init__(self, player_type, name, x, y):
        self.type = player_type  # 0 for human, 1 for computer
        self.name = name  # the name of the specific drone - rigid1 for example
        self.pos = Point(x, y)  # the player's position on the board
        return

    def move(self, new_pos):
        self.pos = new_pos
        return


class Player:
    """
    A class to represent a single player of the game (human VS machine)
    """
    def __init__(self, player_type, target, color):
        self.type = player_type
        self.target = target
        self.color = color
        self.drones = None

    def add_drones(self, drones):
        self.drones = [drone for drone in drones]

    def get_move(self, drone):
        """
        if it's the human player - get direction from user
            otherwise - ask the computer to generate a move using
            the algorithm
        :param player: int - index of player
        :param drone: int - index of drone of player
        :return: void
        """
        if drone.type == "human":
            return self.get_direction()
        else:
            pass

    def get_direction(self):
        """
        Get the move from the player
        :param player: int - index of player
        :param drone: int - index of drone of player
        :return: void
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # Exit at any point by pressing Q
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_LEFT:
                        return "LEFT"
                    if event.key == pygame.K_RIGHT:
                        return "RIGHT"
                    if event.key == pygame.K_UP:
                        return "UP"
                    if event.key == pygame.K_DOWN:
                        return "DOWN"


class Text:
    def __init__(self, text, color):
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont('arial', 30)
        self.surf = self.font.render(text, True, color)

    def update(self, text, color):
        self.surf = self.font.render(self.text, True, BLACK)  # 'erase' old text
        self.surf = self.font.render(text, True, color)
        self.text = text
