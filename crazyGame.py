import logging
import sys
import time

import pygame

import dronesOrchestrator, logger, landmarkManager, joystick
from pygameUtils import button, displayManager
from Games import captureTheFlag, sandbox, grabAllFlags
from Peripherals import dronesController, dronesControllerSimulator, arduinoController

cf_logger = logger.get_logger(__name__, logging_level=logging.DEBUG)

GAMES = {'capture the flag': captureTheFlag.CaptureTheFlag,
         'sandbox': sandbox.DronesControlDemo,
         'grab all flags': grabAllFlags.GrabAllFlags}

games_buttons_images = {'capture the flag': ['button_unpressed_ctf.png', 'button_pressed_ctf.png'],
                         'sandbox': ['droneControl_demo_unpressed.png', 'droneControl_demo_pressed.png'],
                         'grab all flags': ['button_unpressed_cta.png', 'button_pressed_cta.png']}

games_images = {'capture the flag': 'capture_the_flag.png',
                'sandbox': 'capture_the_flag.png',
                'grab all flags': 'capture_the_flag.png'}

MOUSE_LEFT_BUTTON = 1


class CrazyGame:
    def run_crzay_game(self):
        self.initialization_process()

        while True:
            game_name = self.choose_game()
            self.displayManager.text_line.set_text(game_name)
            game = GAMES[game_name]()
            game.joystick = self.joystick
            game.displayManager = self.displayManager
            game.orch = self.orch
            game.landmarks = self.landmarkManager
            game.run()
            if game.quit:
                break
        self.tear_down()

    def initialization_process(self):
        cf_logger.info('start initialization process')
        self.displayManager = displayManager.DisplayManager()
        time.sleep(0.5)
        self.set_arduino_control()
        self.set_drone_controller()
        self.orch = dronesOrchestrator.DronesOrchestrator(self.drone_controller)
        self.landmarkManager = landmarkManager.LandmarkManager(self.arduino_controller,
                                                               self.drone_controller)
        self.displayManager.set_board(self.orch, self.landmarkManager)
        self.displayManager.set_batteries_display(self.orch)
        self.run_starting_animation()

    def set_arduino_control(self):
        cf_logger.info('connecting to arduino board')
        self.displayManager.text_line.set_text('connecting to arduino board')
        try:
            self.arduino_controller = arduinoController.ArduinoController()
        except:
            cf_logger.info('fail to connect arduino board')
            self.displayManager.text_line.set_text('fail to connect to arduino board')
            self.arduino_controller = None
            time.sleep(1)

        self.joystick = joystick.Joystick(self.arduino_controller)

    def set_drone_controller_buttons(self):
        BUTTON_SIZE = (200, 100)
        DIS_FROM_EDGE = 200
        Y_POS = 400
        VM_BUTTON_POS = (DIS_FROM_EDGE, Y_POS)
        DEMO_BUTTON_POS = (displayManager.MAIN_RECT.width - DIS_FROM_EDGE - BUTTON_SIZE[0], Y_POS)

        vm_button = button.Button(VM_BUTTON_POS, BUTTON_SIZE, 'vm')
        demo_button = button.Button(DEMO_BUTTON_POS, BUTTON_SIZE, 'simulator')
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
            else:
                self.drone_controller = dronesControllerSimulator.DronesController()
                cf_logger.info('Connect to drone vm controller...')
            self.displayManager.text_line.set_text('Connect to drone vm controller...')
            try:
                self.drone_controller.connect()
            except ConnectionError:
                fail_text = 'Fail to connect drone %s controller' % drone_controller_type
                cf_logger.info(fail_text)
                self.displayManager.text_line.set_text(fail_text)
                time.sleep(1)
                self.drone_controller = None

    def run_starting_animation(self):
        if not self.drone_controller:
            return

    def set_games_buttons(self):
        BUTTON_SIZE = (320, 120)
        BUTTON_X_POS = 30
        BUTTON_Y_POS = 400
        BUTTONS_X_DISTANCES = BUTTON_SIZE[0] + 30

        self.displayManager.reset_main_rect(True, 'game_menu.png')
        for i, key in enumerate(GAMES):
            pos = (BUTTON_X_POS + BUTTONS_X_DISTANCES*i, BUTTON_Y_POS)
            images = games_buttons_images.get(key)
            temp_button = button.Button(pos, BUTTON_SIZE, key, images[0], images[1], False)
            self.displayManager.add_button(temp_button)

        pos = ((displayManager.MAIN_RECT.width - BUTTONS_X_DISTANCES)//2, displayManager.MAIN_RECT.height - BUTTON_SIZE[1] - 10)
        temp_button = button.Button(pos, BUTTON_SIZE, 'exit', 'exit_unpressed.png', 'exit_pressed.png', False)
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
        if self.arduino_controller:
            self.arduino_controller.disconnect()
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
