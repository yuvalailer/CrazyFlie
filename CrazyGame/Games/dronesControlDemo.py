import pygame
import time

from pygameUtils import displayManager
from pygameUtils import button
from pygameUtils import multiButtons
from pygameUtils import displaysConsts
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

VELOCITY_OFFSET = 0.05
STEP_SIZE_OFFSET = 0.05
BACK_BUTTON_SIZE = (100, 50)
VARIABLE_BUTTON_SIZE = (250, 100)
MATH_OPT_BUTTON_SIZE = (80, 80)
UPDATE_BUTTON_SIZE = (200, 80)

BACK_BUTTON_POS = (50, displayManager.MAIN_RECT.height - 100)
BUTTONS_POS = [(10, 50), (10, 160), (10, 270), (10, 390), (100, 390)]


class DronesControlDemo:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, 'back')
        self.velocity_button = button.Button((10, 50), VARIABLE_BUTTON_SIZE, 'velocity')
        self.step_size_button = button.Button((10, 160), VARIABLE_BUTTON_SIZE, 'step size')
        self.plus_button = button.Button((50, 270), MATH_OPT_BUTTON_SIZE, '+')
        self.minus_button = button.Button((150, 270), MATH_OPT_BUTTON_SIZE, '-')
        self.update_button = button.Button((40, 370), UPDATE_BUTTON_SIZE, 'update')

    def run(self):
        self.velocity = self.orch.drone_velocity
        self.step_size = self.orch.drone_step_size

        self.displayManager.reset_main_rect(update_display=False)
        self.displayManager.board.display = True
        self.add_buttons()
        self.displayManager.render()

        self.current_drone = self.orch.drones[0]
        self.current_drone.color = displaysConsts.GREEN
        self.quit = False
        self.running = True
        self.game_loop()

    def game_loop(self):
        current_time = time.time()
        while self.running:
            if time.time() - current_time > 0.05:
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
                    elif mouse_event_obj[0] == 'point':
                        self.orch.try_goto(self.current_drone, mouse_event_obj[1], blocking=True)
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
        elif button == self.plus_button:
            if self.velocity_button.pressed:
                self.velocity += VELOCITY_OFFSET
            elif self.step_size_button.pressed:
                self.step_size += STEP_SIZE_OFFSET
            self.set_buttons_text()
        elif button == self.minus_button:
            if self.velocity_button.pressed:
                self.velocity -= VELOCITY_OFFSET
            elif self.step_size_button.pressed:
                self.step_size -= STEP_SIZE_OFFSET
            self.set_buttons_text()
        elif button == self.update_button:
            self.orch.set_velocity(self.velocity)
            self.orch.set_drone_step_size(self.step_size)
            text = "Step Size={:.2f}   Velocity={:.2f}".format(self.step_size, self.velocity)
            self.displayManager.text_line.set_text(text)

    def next_drone(self, drone=None):
        self.current_drone.color = displaysConsts.BLACK
        if drone:
            self.current_drone = drone
        else:
            next_drone_index = (self.current_drone.index + 1) % len(self.orch.drones)
            self.current_drone = self.orch.drones[next_drone_index]
        cf_logger.info('change to drone %s' % self.current_drone.name)
        self.current_drone.color = displaysConsts.GREEN

    def add_buttons(self):
        self.displayManager.add_button(self.plus_button)
        self.displayManager.add_button(self.minus_button)
        self.displayManager.add_button(self.update_button)
        self.displayManager.add_button(self.back_button)
        multi_button = multiButtons.MultiButtons([self.velocity_button, self.step_size_button], "velocity and time")
        self.displayManager.add_multi_button(multi_button)

        self.set_buttons_text()

    def set_buttons_text(self):
        self.velocity_button.set_text("velocity=%.2f" % self.velocity)
        self.step_size_button.set_text("step Size=%.2f" % self.step_size)



