import pygame
import numpy as np
import sys

HUMAN = 0
MACHINE = 1

WINDOW_WIDTH = 1000  # width of the program's window, in pixels
WINDOW_HEIGHT = 800  # height in pixels
BOARD_WIDTH = 550  # width of the board's visualization
BOARD_HEIGHT = 550  # height of the board's visualization
SAFE_ZONE = 15.0  # minimal distance between 2 drones

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
        self.players = []  # players is a list of lists, each list is a player containing its drones
        self.width, self.height = width, height
        self.x_margin = int(int(WINDOW_WIDTH / 10))
        self.y_margin = int(int(WINDOW_HEIGHT / 10))
        self.square_x = BOARD_WIDTH//self.width  # the relative movement unit on the board horizontally
        self.square_y = BOARD_HEIGHT//self.height  # the relative movement unit on the board vertically

        self.turn_sign = Text("Turn:  1", BROWN)
        self.time_sign = Text("Time:  0", BROWN)
        self.msg = Text("It's your Turn!", GREEN)

        self.time = 0
        return

    def reset_time(self):
        self.time = pygame.time.get_ticks()

    def add_players(self, player1, player2):
        self.players.append(player1)  # each player is a list
        self.players.append(player2)

    def convert_xy(self, x, y):
        """
        convert real world coordinates to board's coordinates
        where (0,0) is top-right corner of real-world game field
        positive x is directed right and positive y is directed down
        :param x: x coordinate of real-world perspective
        :param y: y coordinate of real-world perspective
        :return: new (x, y) according to game screen perspective
        """
        x_unit = BOARD_WIDTH/self.width
        y_unit = BOARD_HEIGHT/self.height
        new_x = self.x_margin + BOARD_WIDTH - (x * x_unit)
        new_y = self.y_margin + (y * y_unit)
        return new_x, new_y

    def welcome(self):
        font = pygame.font.SysFont('arial', 80)
        surf = font.render("Welcome to The Crazy Game!!!", True, GOLD)
        rect = surf.get_rect()
        center = ((WINDOW_WIDTH-rect.width)//2, (WINDOW_HEIGHT-rect.height)//2)
        self.DISPLAYSURF.blit(surf, center)
        pygame.display.update()

    def draw_board(self, cur_player, cur_drone):

        self.DISPLAYSURF.fill(BLACK)  # clear board (critical to avoid overlapping)

        # the color of the board is green on the human player's turn, and white on the computer's turn
        grid_line_color = WHITE if cur_player else GREEN

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
        for player in range(2):
            for drone in range(2):
                cur = self.players[player][drone]
                if player == cur_player and drone == cur_drone:  # current drone marked blue
                    pygame.draw.circle(self.DISPLAYSURF, BLUE, (int(round(cur.pos[0])), int(round(cur.pos[1]))), 3)
                elif player == HUMAN:  # TODO change player to cur.type
                    pygame.draw.circle(self.DISPLAYSURF, GREEN, (int(round(cur.pos[0])), int(round(cur.pos[1]))), 3)
                else:  # MACHINE player
                    pygame.draw.circle(self.DISPLAYSURF, WHITE, (int(round(cur.pos[0])), int(round(cur.pos[1]))), 3)

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

    def move_player(self, player, direction, x=0, y=0):
        """
        moves player on the board while updating player's info
            unless move isn't valid then an error is printed to the user
        :param player: the Player instance to be moved
        :param direction: String indicating the direction
        :param x: TBD
        :param y: TBD
        :return: 0 if not a valid move, 1 else
        """
        if player.type == HUMAN:  # for the human player
            if direction == "UP":
                new_pos = [player.pos[0], player.pos[1] - self.square_y]
            elif direction == "DOWN":
                new_pos = [player.pos[0], player.pos[1] + self.square_y]
            elif direction == "LEFT":
                new_pos = [player.pos[0] - self.square_x, player.pos[1]]
            elif direction == "RIGHT":
                new_pos = [player.pos[0] + self.square_x, player.pos[1]]
            else:
                print("ERROR: Wrong direction input: " + direction)
                return False
            # validate the move
            if self.is_valid_move(player.name, new_pos):
                player.move(new_pos)
                return True
            else:
                self.msg.update("Illegal move! Try again...", RED)  # indicate the player fo wrong move
                return False

        else:  # for the machine player
            if self.is_valid_move(player.name, [x, y]):
                player.move([x, y])
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
                for drone in player:
                    if name != drone.name:  # then check for collision
                        if np.linalg.norm([drone.pos[i]-new_pos[i] for i in range(2)]) <= SAFE_ZONE:
                            return False
            return True
        return False

    def is_in_board(self, new_pos):
        """
        helper function to is_valid_move
        :param new_pos: list [x, y]
        :return: True if new_pos is inside the board, False otherwise
        """
        return self.x_margin <= new_pos[0] <= BOARD_WIDTH+self.x_margin \
            and self.y_margin <= new_pos[1] <= self.y_margin+BOARD_HEIGHT

    def get_move(self, player, drone):
        """
        if it's the human player - get direction from user
            otherwise - ask the computer to generate a move using
            the algorithm
        :param player: int - index of player
        :param drone: int - index of drone of player
        :return: void
        """
        # TODO TEMP
        self.get_move_human(player, drone)
        if player == 0:
            self.msg.update("Player 2's Turn! Go Ahead", WHITE)
        else:
            self.msg.update("Player 1's Turn! Go Ahead", GREEN)
        # TODO END TEMP

        # TODO delete temp and uncomment this when MACHINE implemented
        '''
        if self.players[player][drone].type == HUMAN:  # Human turn
            self.get_move_human(player, drone)
            self.msg.update("Computer's Turn! Please wait", WHITE)
        else:  # player == MACHINE
            self.msg.update("It's your Turn!", GREEN)
        '''
        # update turns:
        self.turns += 1
        self.turn_sign.update("Turn:  "+str(self.turns), BROWN)

    def get_move_human(self, player, drone):
        """
        Get the move from the player
        :param player: int - index of player
        :param drone: int - index of drone of player
        :return: void
        """
        cur = self.players[player][drone]  # get the Player instance of current playing drone
        valid = False  # loop indicator
        while not valid:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # Exit at any point by pressing Q
                        pygame.quit()
                        sys.exit()
                    # If the move was good, valid will turn True
                    # and the loop will terminate and the turn will be over
                    if event.key == pygame.K_LEFT:
                        valid = self.move_player(cur, "LEFT")
                    if event.key == pygame.K_RIGHT:
                        valid = self.move_player(cur, "RIGHT")
                    if event.key == pygame.K_UP:
                        valid = self.move_player(cur, "UP")
                    if event.key == pygame.K_DOWN:
                        valid = self.move_player(cur, "DOWN")
            self.draw_board(player, drone)  # NOTICE: this line happens even if the player doesn't press nothing


class Player:
    """
    A class to represent a single entity of the game (drone)
    """
    def __init__(self, player_type, name, x, y):
        self.type = player_type  # 0 for human, 1 for computer
        self.name = name  # the name of the specific drone - rigid1 for example
        self.pos = [x, y]  # the player's position on the board
        return

    def move(self, new_pos):
        self.pos = new_pos
        return


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
