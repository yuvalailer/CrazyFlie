import game_utils as gu
from game_utils import *


def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


def run_game():
    # Plays a single game of reversi each time this function is called.

    # create the board and the players
    board = Board()
    player1 = {"rigid1": (0, board.board_height / 2 - 1), "rigid2": (0, board.board_height / 2)}
    player2 = {"rigid3": (board.board_width - 1, board.board_height / 2 - 1), "rigid4": (board.board_width - 1, board.board_height / 2)}
    board.add_players(player1, player2)

    # Draw the starting board
    board.draw_board()

    # Game on!
    game_loop()


def main():
    print("Welcome to The Crazy Game")
    run_game()




main()