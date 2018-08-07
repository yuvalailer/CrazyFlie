from game_utils import *
import sys

NUM_DRONES = 2

def quit_game():
    pygame.quit()
    sys.exit()


def game_loop(board):
    game_is_on = True
    board.reset_time()  # start the clock
    while game_is_on:
        for player in board.players:  # circulate between players
            drone = board.choose_drone(player)
            move = player.get_move(drone)
            board.move_drone(drone, move)
            if drone.pos == player.target:
                board.finish()
            for event in pygame.event.get():  # TODO: able to quit at any time?
                if event.type == pygame.QUIT:
                    game_is_on = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_is_on = False
    quit_game()


def run_game():
    # create the board and the players
    board = Board(10, 10)

    # create players
    human = Player("human", Point(board.convert_xy(0, 0)), GREEN)
    x1, y1 = board.convert_xy(0, board.height / 2)
    x2, y2 = board.convert_xy(0, board.height / 2 + 1)
    d1 = Drone("human", "rigid1", x1, y1)
    if NUM_DRONES == 4:
        d2 = Drone("human", "rigid2", x2, y2)
        human.add_drones([d1, d2])
    else:
        human.add_drones([d1])

    machine = Player("machine", Point(board.convert_xy(10, 10)), RED)
    x3, y3 = board.convert_xy(board.width, board.height / 2)
    x4, y4 = board.convert_xy(board.width, board.height / 2 + 1)
    d3 = Drone("human", "rigid3", x3, y3)  # TODO change to MACHINE
    if NUM_DRONES == 4:
        d4 = Drone("human", "rigid4", x4, y4)  # TODO change to MACHINE
        machine.add_drones([d3, d4])
    else:
        machine.add_drones([d3])

    board.add_players(human, machine)

    # Draw the starting board
    pygame.display.set_caption('Crazy Hell Game')
    board.welcome()
    pygame.time.wait(2000)
    board.draw_board()

    # Game on!
    game_loop(board)


def main():
    pygame.init()
    run_game()


if __name__ == "__main__":
    main()
