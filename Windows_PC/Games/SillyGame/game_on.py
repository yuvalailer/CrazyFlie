import sys
sys.path.insert(0, '..')
from game_utils import *
sys.path.insert(0, '..\..')
import logger
from dronesControllerAPI import DronesControllerAPI
cf_logger = logger.get_logger(__name__)  # debug(), info(), warning(), error(), exception(), critical()

NUM_DRONES = 4
VM_IP = "172.16.1.2"
AVAILABLE_DRONES = ["crazyflie2", "crazyflie1", "crazyflie3", "crazyflie4"]


def quit_game():
    pygame.quit()
    sys.exit()


def game_loop(board, dronesController):
    game_is_on = True
    board.reset_time()  # start the clock
    while game_is_on:
        for player in board.players:  # circulate between players
            drone = board.choose_drone(player)

            valid = False
            while not valid:
                move = player.get_move(drone, board)
                valid = board.move_drone(drone, move)
            # Send to VM
            loop_status = dronesController.send("{}${}".format(drone.name, move))  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            if loop_status == 1:
                cf_logger.error("dronesControllerTester: Failed to execute command: {}".format(move))
                # TODO # what to do?
            elif loop_status == -1:
                cf_logger.critical("Communication error")
                # TODO # Print "Communication error" to the screen
                break
            if drone.pos == player.target:
                board.finish()
                wait_for_press()
                game_is_on = False
                break
            for event in pygame.event.get():  # TODO: able to quit at any time?
                if event.type == pygame.QUIT:
                    game_is_on = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_is_on = False
    quit_game()


def wait_for_press():
    while True:
        for event in pygame.event.get():  # TODO: able to quit at any time?
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                return


def run_game():
    # create the board and the players
    board = Board(8, 7)
    #
    dronesController = DronesControllerAPI(ip=VM_IP)  # Optional variables: "ip", "port" and "buffer_size"
    if not dronesController.connect():  # Return True on success and False otherwise
        cf_logger.critical("Communication error")
        # TODO # Print "Communication error" to the screen and then "quit_game"
        return False
    # create players
    human = Player("human", Point(board.convert_xy(0, 0)))
    machine = Player("machine", Point(board.convert_xy(8, 7)))
    x1, y1 = 0, board.height / 2
    x3, y3 = board.width, board.height / 2
    d1 = Drone("human", AVAILABLE_DRONES[0], x1, y1, GREEN)
    d3 = Drone("human", AVAILABLE_DRONES[2], x3, y3, RED)  # TODO change to MACHINE
    if NUM_DRONES == 4:
        x2, y2 = 0, board.height / 2 + 1
        x4, y4 = board.width, board.height / 2 + 1
        d2 = Drone("human", AVAILABLE_DRONES[1], x2, y2, GREEN)
        d4 = Drone("human", AVAILABLE_DRONES[3], x4, y4, RED)  # TODO change to MACHINE
        human.add_drones([d1, d2])
        machine.add_drones([d3, d4])
        board.add_drones([d1, d2, d3, d4])
    else:
        human.add_drones([d1])
        machine.add_drones([d3])
        board.add_drones([d1, d3])
    board.add_players(human, machine)
    # Register drones
    for drone in board.drones_set:
        if dronesController.send("{}$Register".format(drone.name)) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO # Print error and then "quit_game"
            return False
        if dronesController.send("{}$TakeOff${}${}".format(drone.name, int(drone.pos.x), int(drone.pos.y))) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO # Print error and then "quit_game"
            return False
    # Draw the starting board
    pygame.display.set_caption('Crazy Hell Game')
    board.welcome()
    pygame.time.wait(2000)
    board.DISPLAYSURF.fill(BLACK)  # clear board
    board.draw_board()
    # Game on!
    game_loop(board, dronesController)
    # Land and Unregister
    for drone in board.drones_set:
        if dronesController.send("{}$Land".format(drone.name)) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO # Print error and then "quit_game"
            return False
        if dronesController.send("{}$UnRegister".format(drone.name)) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO # Print error and then "quit_game"
            return False


def main():
    pygame.init()
    run_game()


if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()
