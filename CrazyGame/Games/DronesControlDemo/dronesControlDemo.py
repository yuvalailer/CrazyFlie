import pygame
import time

from pygameUtils import drawer
from pygameUtils import button
from pygameUtils import displaysConsts
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

BACK_BUTTON_SIZE = (100, 50)
BACK_BUTTON_POS = (50, drawer.MAIN_RECT.height - 100)


class DronesControlDemo:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, 'back')

    def run(self):
        self.drawer.reset_main_rect(update_display=False)
        self.drawer.add_button(self.back_button)
        self.drawer.render()
        self.current_drone_index = -1
        self.current_drone = None

        current_time = time.time()
        while True:
            if time.time() - current_time > 0.1:
                self.orch.update_drones_positions()
                self.drawer.render()
                joystick_dir = self.joystick.get_normalize_direction()
                if self.current_drone:
                    self.orch.try_move_drone(self.current_drone, joystick_dir)
                current_time = time.time()

            event_result = self.manage_events()
            if event_result:
                if event_result[0] == 'exit':
                    return event_result[1]
                if event_result[0] == 'button':
                    if event_result[1] == self.back_button:
                        if self.current_drone:
                            self.current_drone.color = displaysConsts.BLACK
                            self.orch.land(self.current_drone)
                            self.current_drone_index = -1
                            self.current_drone = None
                        return 'game ended'

                elif event_result[0] == 'drone':
                    if self.current_drone:
                        self.current_drone.color = displaysConsts.BLACK
                    self.current_drone = event_result[1]
                    self.current_drone.color = displaysConsts.GREEN

                elif event_result[0] == 'point':
                    pass # TODO

    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit', 'exit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawer.check_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                return self.drawer.check_mouse_event(event.type)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.next_drone()
                elif event.key == pygame.K_u:
                    self.orch.try_take_off(self.current_drone)
                elif event.key == pygame.K_l:
                    self.orch.land(self.current_drone)
        return None

    def next_drone(self):
        self.current_drone.color = displaysConsts.BLACK
        self.current_drone_index = (self.current_drone_index + 1) % len(self.orch.drones)
        self.current_drone = self.orch.drones[self.current_drone_index]
        cf_logger.info('change to drone %s'%self.current_drone.name)
        self.current_drone.color = displaysConsts.GREEN

