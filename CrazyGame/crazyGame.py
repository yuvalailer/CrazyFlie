import logging
import sys
import time
import pygame

from CrazyGame import dronesOrchestrator, joystick, logger
from pygameUtils import button, displayManager
from Games import captureTheFlag, joystickDemo, dronesControlDemo
from Peripherals import controlBoard, dronesController, dronesControllerSimulator

cf_logger = logger.get_logger(__name__, logging_level=logging.DEBUG)

GAMES = {'capture the flag': captureTheFlag.CaptureTheFlag,
         'joystick demo': joystickDemo.JoystickDemo,
         'drones control demo': dronesControlDemo.DronesControlDemo}

MOUSE_LEFT_BUTTON = 1


class CrazyGame:
    def run_crzay_game(self):
        self.initialization_process()

        while True:
            self.displayManager.reset_main_rect()
            game_name = self.choose_game()
            self.displayManager.reset_main_rect()
            self.displayManager.text_line.set_text(game_name)
            game = GAMES[game_name]()
            game.joystick = self.joystick
            game.droneController = self.drone_controller
            game.displayManager = self.displayManager
            game.orch = self.orch
            game.run()
            if game.quit:
                break
        self.tear_down()

    def initialization_process(self):
        cf_logger.info('start initialization process')
        self.displayManager = displayManager.DisplayManager()
        time.sleep(0.5)
        self.set_control_board()
        self.set_drone_controller()
        self.orch = dronesOrchestrator.DronesOrchestrator(self.drone_controller)
        self.displayManager.set_board(self.orch)
        self.run_starting_animation()

    def set_control_board(self):
        cf_logger.info('connecting to control board')
        self.displayManager.text_line.set_text('connecting to control board')
        try:
            self.control_board = controlBoard.ControlBoard()
        except:
            cf_logger.info('fail to connect control board')
            self.displayManager.text_line.set_text('connecting to control board')
            self.control_board = None

        self.joystick = joystick.Joystick(self.control_board)

    def set_drone_controller_buttons(self):
        BUTTON_SIZE = (200, 100)
        DIS_FROM_EDGE = 200
        Y_POS = 400
        VM_BUTTON_POS = (DIS_FROM_EDGE, Y_POS)
        DEMO_BUTTON_POS = (displayManager.MAIN_RECT.width - DIS_FROM_EDGE - BUTTON_SIZE[0], Y_POS)

        vm_button = button.Button(VM_BUTTON_POS, BUTTON_SIZE, 'vm')
        demo_button = button.Button(DEMO_BUTTON_POS, BUTTON_SIZE, 'demo')
        self.displayManager.add_button(vm_button)
        self.displayManager.add_button(demo_button)
        self.displayManager.render()

    def get_drone_controller_type(self):
        self.set_drone_controller_buttons()

        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.tear_down()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT_BUTTON:
                self.displayManager.handle_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == MOUSE_LEFT_BUTTON:
                mouse_event_obj = self.displayManager.handle_mouse_event(event.type)
                if not mouse_event_obj:
                    continue
                if mouse_event_obj[0] == 'button':
                    button = mouse_event_obj[1]
                    cf_logger.debug('button %s clicked' % button.text)
                    if button.text == 'exit':
                        self.tear_down()
                    return button.text

    def set_drone_controller(self):
        self.drone_controller = None
        while not self.drone_controller:
            self.displayManager.text_line.set_text('Choose drones controller')
            drone_controller_type = self.get_drone_controller_type()
            if drone_controller_type == 'vm':
                self.drone_controller = dronesController.DronesController()
                cf_logger.info('Connect to drone vm controller...')
                self.displayManager.text_line.set_text('Connect to drone vm controller...')
                try:
                    self.drone_controller.connect()
                except ConnectionError:
                    cf_logger.info('Fail to connect drone vm controller')
                    self.displayManager.text_line.set_text('Failed')
                    time.sleep(1)
                    self.drone_controller = None
            elif drone_controller_type == 'demo':
                cf_logger.info('Connect to demo drone controller...')
                self.drone_controller = dronesControllerSimulator.DronesController()

    def run_starting_animation(self):
        if not self.drone_controller:
            return

    def set_games_buttons(self):
        BUTTON_SIZE = (400, 100)
        BUTTON_X_POS = self.displayManager.display_surf.get_width() / 2 - BUTTON_SIZE[0] / 2
        BUTTON_Y_START_POS = 100
        BUTTONS_Y_DISTANCES = 150

        self.displayManager.reset_main_rect()
        for i, key in enumerate(GAMES):
            pos = (BUTTON_X_POS, BUTTON_Y_START_POS + i * BUTTONS_Y_DISTANCES)
            temp_button = button.Button(pos, BUTTON_SIZE, key)
            self.displayManager.add_button(temp_button)

        pos = (BUTTON_X_POS, displayManager.MAIN_RECT.height - BUTTON_SIZE[1] - 50)
        temp_button = button.Button(pos, BUTTON_SIZE, 'exit', 'button_unpressed_exit.png', 'button_pressed_exit.png')
        self.displayManager.add_button(temp_button)
        self.displayManager.render()

    def choose_game(self):
        self.displayManager.text_line.set_text('choose your game')
        self.displayManager.board.display = False
        self.set_games_buttons()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.tear_down()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT_BUTTON:
                self.displayManager.handle_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == MOUSE_LEFT_BUTTON:
                mouse_event_obj = self.displayManager.handle_mouse_event(event.type)
                if not mouse_event_obj:
                    continue
                if mouse_event_obj[0] == 'button':
                    button = mouse_event_obj[1]
                    cf_logger.debug('button %s clicked' % button.text)
                    if button.text == 'exit':
                        self.tear_down()
                    return button.text

    def tear_down(self):
        if self.control_board:
            self.control_board.disconnect()
        if self.drone_controller:
            self.drone_controller.disconnect()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####            Started crazy game                ####")
    cf_logger.info("######################################################")
    cg = CrazyGame()
    cg.run_crzay_game()
