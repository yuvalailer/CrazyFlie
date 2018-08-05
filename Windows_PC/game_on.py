import pygame
from game_utils import *
import sys


def game_loop(board):
    game_is_on = True
    board.reset_time()  # start the clock
    while game_is_on:
        for drone in range(2):  # circulate between the two drones each player has
            for player in range(2):  # circulate between players for that drone
                board.get_move(player, drone)
                for event in pygame.event.get():  # TODO: able to quit at any time?
                    if event.type == pygame.QUIT:
                        game_is_on = False
                    if event.type == pygame.event.KEYDOWN:
                        if event.key == pygame.K_q:
                            game_is_on = False
    pygame.quit()
    sys.exit()


def run_game():
    # create the board and the players
    board = Board(11, 11)

    # create players
    x1, y1 = board.convert_xy(0, board.height / 2)
    x2, y2 = board.convert_xy(0, board.height / 2 + 1)
    p1 = Player(HUMAN, "rigid1", x1, y1)
    p2 = Player(HUMAN, "rigid2", x2, y2)
    human = [p1, p2]

    x3, y3 = board.convert_xy(board.width, board.height / 2)
    x4, y4 = board.convert_xy(board.width, board.height / 2 + 1)
    p3 = Player(HUMAN, "rigid3", x3, y3)  # TODO change to MACHINE
    p4 = Player(HUMAN, "rigid4", x4, y4)  # TODO change to MACHINE
    machine = [p3, p4]

    board.add_players(human, machine)

    # Draw the starting board
    pygame.display.set_caption('Crazy Hell Game')
    board.welcome()
    pygame.time.wait(2000)
    board.draw_board(0, 0)

    # Game on!
    game_loop(board)


def main():
    pygame.init()
    run_game()


if __name__ == "__main__":
    main()
