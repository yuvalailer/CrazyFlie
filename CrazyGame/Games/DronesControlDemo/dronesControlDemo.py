import pygame
import time

from pygameUtils import drawer
from pygameUtils import button
from pygameUtils import multiButton
from pygameUtils import displaysConsts
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)




class DronesControlDemo:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, 'back')


    def create_buttons(self):

        self.drawer.add_button(self.plus_button)
        self.drawer.add_button(self.minus_button)
        self.drawer.add_button(self.update_button)
        multi_button = multiButton.MultiButton([self.velocity_button, self.step_size_button], "velocity and time")
        self.drawer.add_multi_button(multi_button)

    def run(self):
        self.drawer.reset_main_rect(update_display=False)
        self.drawer.add_button(self.back_button)
        self.drawer.render()
        self.current_drone_index = 0
        self.current_drone = self.orch.drones[self.current_drone_index]
        self.current_drone.color = displaysConsts.GREEN
        self.velocity = self.orch.drone_velocity
        self.step_size = self.orch.drone_move_time_out
        self.create_demo_buttons()
        self.drawer.render()
        current_time = time.time()
        while True:
            if time.time() - current_time > 0.1:
                self.orch.update_drones_positions()
                self.drawer.render()
                joystick_dir = self.joystick.get_normalize_direction()
                self.orch.try_move_drone(self.current_drone, joystick_dir)
                current_time = time.time()

            event_result = self.manage_events()
            if event_result != 'continue':
                return event_result

    def manage_events(self):
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawer.check_buttons_mouse_event(event.type)
                self.handle_buttons(pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = self.drawer.check_buttons_mouse_event(event.type)
                if button == self.back_button:
                    return 'game ended'
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.next_drone()

                elif event.key == pygame.K_u:
                    self.orch.try_take_off(self.current_drone)
                elif event.key == pygame.K_l:
                    self.orch.land(self.current_drone)
        return 'continue'

    def handle_buttons(self, pos):


    def next_drone(self):
        self.current_drone.color = displaysConsts.BLACK
        self.current_drone_index = (self.current_drone_index + 1) % len(self.orch.drones)
        self.current_drone = self.orch.drones[self.current_drone_index]
        cf_logger.info('change to drone %s'%self.current_drone.name)
        self.current_drone.color = displaysConsts.GREEN

