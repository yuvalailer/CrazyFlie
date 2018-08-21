import pygame
import time

from pygameUtils import displayManager
from pygameUtils import button
from pygameUtils import displaysConsts
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

BACK_BUTTON_SIZE = (100, 50)
BACK_BUTTON_POS = (50, displayManager.MAIN_RECT.height - 100)


class DronesControlDemo:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, 'back')

    def run(self):
        self.displayManager.reset_main_rect(update_display=False)
        self.displayManager.add_button(self.back_button)
        self.displayManager.board.display = True
        self.displayManager.render()
        self.current_drone = self.orch.drones[0]
        self.current_drone.color = displaysConsts.GREEN

        self.displayManager.render()
        self.quit = False
        self.running = True
        self.game_loop()

    def game_loop(self):
        current_time = time.time()
        while self.running:
            if time.time() - current_time > 0.1:
                self.orch.update_drones_positions()
                self.displayManager.render()
                joystick_dir = self.joystick.get_normalize_direction()
                self.orch.try_move_drone(self.current_drone, joystick_dir)
                current_time = time.time()

            self.manage_events()

    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.displayManager.handle_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_event_obj = self.displayManager.handle_mouse_event(event.type)
                if mouse_event_obj:
                    if mouse_event_obj[0] == 'button':
                        self.manage_button_click(mouse_event_obj[1])
                    elif mouse_event_obj[0] == 'drone':
                        self.next_drone(mouse_event_obj[1])
            elif event.type == pygame.KEYUP:
                self.manage_keyboard_event(event.key)

    def manage_keyboard_event(self, key):
        if key == pygame.K_SPACE:
            self.next_drone()
        elif key == pygame.K_u:
            self.orch.try_take_off(self.current_drone)
        elif key == pygame.K_l:
            self.orch.land(self.current_drone)

    def manage_button_click(self, button):
        if button == self.back_button:
            self.running = False

    def next_drone(self, drone=None):
        self.current_drone.color = displaysConsts.BLACK
        if drone:
            self.current_drone = drone
        else:
            next_drone_index = self.current_drone.index + 1 % len(self.orch.drones)
            self.current_drone = self.orch.drones[next_drone_index]
        cf_logger.info('change to drone %s' % self.current_drone.name)
        self.current_drone.color = displaysConsts.GREEN



