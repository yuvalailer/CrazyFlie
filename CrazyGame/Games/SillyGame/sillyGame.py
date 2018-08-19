from CrazyGame import logger
from CrazyGame.Games import dronesBoard

cf_logger = logger.get_logger(__name__)

NUM_DRONES = 4
AVAILABLE_DRONES = ["crazyflie2", "crazyflie1", "crazyflie3", "crazyflie4"]


class SillyGame():
    def __init__(self):
        self.board = dronesBoard.Board()

    def run(self):
        pass



def game_loop(board, dronesController):
    game_is_on = True
    board.reset_time()  # Start the clock
    while game_is_on:
        for player in board.players:  # Circulate between players
            drone = board.choose_drone(player)
            valid = False
            while not valid:
                move = player.get_move(drone, board)
                valid = board.move_drone(drone, move)
            # Send to VM
            loop_status = dronesController.send("{}${}".format(drone.name,
                                                               move))  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            if loop_status == 1:
                cf_logger.error("dronesControllerTester: Failed to execute command: {}".format(move))
            # TODO - What to do?
            elif loop_status == -1:
                cf_logger.critical("Communication error")
                # TODO - Print "Communication error" to the screen
                break
            if drone.pos == player.target:
                board.finish()
                wait_for_press()
                game_is_on = False
                break
            for event in pygame.event.get():  # TODO - Able to quit at any time?
                if (event.type == pygame.QUIT) or ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_q)):
                    game_is_on = False
    quit_game()


def wait_for_press():
    while True:
        for event in pygame.event.get():  # TODO - Able to quit at any time?
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                return


def run_game():
    # Create the board and the players
    board = Board(8, 7)
    # Open connection to the VM
    dronesController = DronesControllerAPI(ip=VM_IP)  # Optional variables: "ip", "port" and "buffer_size"
    if not dronesController.connect():  # Return True on success and False otherwise
        cf_logger.critical("Communication error")
        # TODO - Print/log "Communication error" to the screen and then "quit_game"
        return False
    # Create players
    human = Player("human", Point(board.convert_xy(0, 0)))
    machine = Player("machine", Point(board.convert_xy(8, 7)))
    x1, y1 = 0, board.height / 2
    x3, y3 = board.width, board.height / 2
    d1 = Drone("human", AVAILABLE_DRONES[0], x1, y1, GREEN)
    d3 = Drone("human", AVAILABLE_DRONES[2], x3, y3, RED)  # TODO - Change to MACHINE
    if NUM_DRONES == 4:
        x2, y2 = 0, board.height / 2 + 1
        x4, y4 = board.width, board.height / 2 + 1
        d2 = Drone("human", AVAILABLE_DRONES[1], x2, y2, GREEN)
        d4 = Drone("human", AVAILABLE_DRONES[3], x4, y4, RED)  # TODO - Change to MACHINE
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
        if dronesController.send("{}$Register".format(
                drone.name)) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO - Print/log error and then "quit_game"
            return False
        if dronesController.send("{}$TakeOff${}${}".format(drone.name, int(drone.pos.x), int(
                drone.pos.y))) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO - Print/log error and then "quit_game"
            return False
    # Draw the starting board
    pygame.display.set_caption("Crazy Hell Game")
    board.welcome()
    pygame.time.wait(2000)
    board.DISPLAYSURF.fill(BLACK)  # Clear board
    board.draw_board()
    # Game on!
    game_loop(board, dronesController)
    # Land and Unregister
    for drone in board.drones_set:
        if dronesController.send("{}$Land".format(
                drone.name)) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO - Print/log error and then "quit_game"
            return False
        if dronesController.send("{}$UnRegister".format(
                drone.name)) != 0:  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
            # TODO - Print/log error and then "quit_game"
            return False