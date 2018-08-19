import logging
import sys
import time

import pygame

import drawer
from CrazyGame import controlBoard
from CrazyGame import dronesController
from CrazyGame import joystick
from CrazyGame import logger
from CrazyGame.Games.JoystickDemo import joystickDemo
from CrazyGame.Games.SillyGame import sillyGame

cf_logger = logger.get_logger(__name__, logging_level=logging.DEBUG)

GAMES = {'silly game':sillyGame.SillyGame,
         'joystick demo': joystickDemo.JoystickDemo, }


class CrazyGame():
    def run_crzay_game(self):
        self.initialization_process()

        while True:
            game_name = self.choose_game()
            game = GAMES[game_name]()
            game.joystick = self.joystick
            game.droneController = self.drone_controller
            game.drawer = self.drawer
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

    def set_drone_controller(self):
        cf_logger.info('connect to drone vm controller...')
        self.drawer.set_text_line('connecting to drone vm controller')
        self.drone_controller = dronesController.DronesController()
        try:
            self.drone_controller.connect()
            cf_logger.info('connection to drone vm controller established')
        except ConnectionError:
            cf_logger.info('fail to connect drone vm controller')
            self.drone_controller = None

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
