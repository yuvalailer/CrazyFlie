import logging
import sys
import time

import pygame

from CrazyGame import controlBoard
from CrazyGame import dronesController
from CrazyGame import dronesControllerSimulator
from CrazyGame import joystick
from CrazyGame import logger
from CrazyGame.Games import dronesOrchestrator
from CrazyGame.Games.JoystickDemo import joystickDemo
from CrazyGame.Games.SillyGame import sillyGame
from CrazyGame.Games.DronesControlDemo import dronesControlDemo
from CrazyGame.pygameUtils import drawer
from CrazyGame.pygameUtils import displayBoard

cf_logger = logger.get_logger(__name__, logging_level=logging.DEBUG)

GAMES = {'silly game': sillyGame.SillyGame,
         'joystick demo': joystickDemo.JoystickDemo,
         'drones control demo': dronesControlDemo.DronesControlDemo}


class CrazyGame:
    def run_crzay_game(self):
        self.initialization_process()

        while True:
            game_name = self.choose_game()
            game = GAMES[game_name]()
            game.joystick = self.joystick
            game.droneController = self.drone_controller
            game.drawer = self.drawer
            game.orch = self.orch
            game_result = game.run()
            if game_result == 'exit':
                break
        self.tear_down()

    def initialization_process(self):
        cf_logger.info('start initialization process')
        self.drawer = drawer.Drawer()
        time.sleep(0.5)
        self.set_control_board()
        self.set_drone_controller()
        self.orch = dronesOrchestrator.DronesOrchestrator(self.drone_controller.get_world_size())
        self.orch.add_drones(self.drone_controller.get_objects())  # TODO -> support other object than drone
        self.drawer.set_board(self.orch)
        self.run_starting_animation()

    def set_control_board(self):
        cf_logger.info('connecting to control board')
        self.drawer.set_text_line('connecting to control board')
        try:
            self.control_board = controlBoard.ControlBoard()
        except:
            cf_logger.info('fail to connect control board')
            self.drawer.set_text_line('connecting to control board')
            self.control_board = None

        self.joystick = joystick.Joystick(self.control_board)

    def set_drone_controller_buttons(self):
        BUTTON_SIZE = (200, 100)
        DIS_FROM_EDGE = 200
        Y_POS = 400
        VM_BUTTON_POS = (DIS_FROM_EDGE, Y_POS)
        DEMO_BUTTON_POS = (drawer.MAIN_RECT.width - DIS_FROM_EDGE - BUTTON_SIZE[0], Y_POS)

        self.drawer.add_button(drawer.Button(VM_BUTTON_POS, BUTTON_SIZE, 'vm'))
        self.drawer.add_button(drawer.Button(DEMO_BUTTON_POS, BUTTON_SIZE, 'demo'))

        self.drawer.render_buttons()

    def get_drone_controller_type(self):
        self.set_drone_controller_buttons()

        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.tear_down()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawer.check_buttons_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = self.drawer.check_buttons_mouse_event(event.type)
                if button:
                    cf_logger.debug('button %s clicked' % button.text)
                    if button.text == 'exit':
                        self.tear_down()
                    return button.text

    def set_drone_controller(self):
        self.drone_controller = None
        while not self.drone_controller:
            self.drawer.set_text_line('choose drones controller', update_display=False)
            drone_controller_type = self.get_drone_controller_type()
            if drone_controller_type == 'vm':
                self.drone_controller = dronesController.DronesController()
                cf_logger.info('connect to drone vm controller...')
                try:
                    self.drone_controller.connect()
                except ConnectionError:
                    cf_logger.info('fail to connect drone vm controller')
                    self.drone_controller = None
            elif drone_controller_type == 'demo':
                cf_logger.info('connect to demo drone controller...')
                self.drone_controller = dronesControllerSimulator.DronesController()

    def run_starting_animation(self):
        if not self.drone_controller:
            return

    def set_games_buttons(self):
        BUTTON_SIZE = (400, 100)
        BUTTON_X_POS = self.drawer.display_surf.get_width() / 2 - BUTTON_SIZE[0] / 2
        BUTTON_Y_START_POS = 100
        BUTTONS_Y_DISTANCES = 150

        self.drawer.reset_main_rect()
        for i, key in enumerate(GAMES):
            pos = (BUTTON_X_POS, BUTTON_Y_START_POS + i * BUTTONS_Y_DISTANCES)
            button = drawer.Button(pos, BUTTON_SIZE, key)
            self.drawer.add_button(button)

        pos = (BUTTON_X_POS, drawer.MAIN_RECT.height - BUTTON_SIZE[1] - 50)
        button = drawer.Button(pos, BUTTON_SIZE, 'exit')
        self.drawer.add_button(button)
        self.drawer.render_buttons()

    def choose_game(self):
        self.drawer.set_text_line('choose your game', update_display=False)
        self.set_games_buttons()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.tear_down()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawer.check_buttons_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = self.drawer.check_buttons_mouse_event(event.type)
                if button:
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
