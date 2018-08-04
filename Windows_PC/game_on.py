import game_utils as gu
from game_utils import *
import sys


def game_loop():
    while True:
        for event in pygame.event.get(): ##### TODO: able to quit at any time?
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


def run_game():
    # create the board and the players
    board = Board(11, 11)

    # create players
    x1, y1 = board.convert_xy(0, board.height / 2)
    x2, y2 = board.convert_xy(0, board.height / 2 + 1)
    p1 = Player(1, "rigid1", x1, y1)
    p2 = Player(1, "rigid2", x2, y2)
    human = [p1, p2]

    x3, y3 = board.convert_xy(board.width, board.height / 2)
    x4, y4 = board.convert_xy(board.width, board.height / 2 + 1)
    p3 = Player(0, "rigid3", x3, y3)
    p4 = Player(0, "rigid4", x4, y4)
    machine = [p3, p4]

    board.add_players(human, machine)

    # Draw the starting board
    board.draw_board()

    # Game on!
    game_loop()


def main():
    print("Welcome to The Crazy Game")
    run_game()


if __name__ == "__main__":
    main()
