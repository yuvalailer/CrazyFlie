import pygame
import time
from munch import Munch
from shapely.geometry import Point

from pygameUtils import displayManager
from pygameUtils import button
from pygameUtils import multiButtons
from pygameUtils import displaysConsts
import logger

cf_logger = logger.get_logger(__name__)

VELOCITY_OFFSET = 0.05
STEP_SIZE_OFFSET = 0.05
BACK_BUTTON_SIZE = (250, 100)
VARIABLE_BUTTON_SIZE = (250, 100)
MATH_OPT_BUTTON_SIZE = (80, 80)
UPDATE_BUTTON_SIZE = (200, 80)
X_MIDDLE_POS = 80
Y_HIGHEST_POS = 100
BACK_BUTTON_POS = (80, displayManager.MAIN_RECT.height - BACK_BUTTON_SIZE[1] - 20)


class DronesControlDemo:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, '', 'back.png', 'back_pressed.png')
        self.velocity_button = button.Button((X_MIDDLE_POS, Y_HIGHEST_POS), VARIABLE_BUTTON_SIZE, 'velocity')
        self.step_size_button = button.Button((X_MIDDLE_POS, Y_HIGHEST_POS + 110), VARIABLE_BUTTON_SIZE, 'step size')
        self.plus_button = button.Button((X_MIDDLE_POS + 40, Y_HIGHEST_POS + 220), MATH_OPT_BUTTON_SIZE, '+')
        self.minus_button = button.Button((X_MIDDLE_POS + MATH_OPT_BUTTON_SIZE[0] + 50, Y_HIGHEST_POS + 220), MATH_OPT_BUTTON_SIZE, '-')
        self.update_button = button.Button((X_MIDDLE_POS + 20, Y_HIGHEST_POS + 310), UPDATE_BUTTON_SIZE, 'update')

    def run(self):
        self.velocity = self.orch.drone_velocity
        self.step_size = self.orch.drone_step_size

        if not self.landmarks.real_leds:
            self.set_virtual_leds()

        self.displayManager.reset_main_rect(True, 'scaled_blue.png')
        self.displayManager.board.display = True
        self.displayManager.batteriesDisplay.display = True
        self.add_buttons()
        self.displayManager.render(render_batteries=True)

        self.current_drone = self.orch.drones[0]
        self.led = None
        self.current_drone.color = displaysConsts.GREEN
        self.quit = False
        self.running = True
        self.game_loop()

    def game_loop(self):
        current_time = time.time()
        while self.running:
            if time.time() - current_time > 0.07:
                self.orch.update_drones_positions()
                self.displayManager.render()
                joystick_dir = self.joystick.get_normalize_direction()
                if joystick_dir:
                    self.orch.try_move_drone(self.current_drone, joystick_dir)
                current_time = time.time()

            self.manage_events()
        self.orch.stop_drone(self.current_drone)

    # If there are no real LEDs that can be captures by the cameras, we create them in the simulator manually
    def set_virtual_leds(self):
        self.landmarks.leds = [Munch(name='led1', number=0,
                                     position=Point(self.orch.max_x - self.orch.drone_radius,
                                                    (self.orch.max_y + self.orch.min_y) / 2)),
                               Munch(name='led2', number=1,
                                     position=Point(self.orch.min_x + self.orch.drone_radius,
                                                    (self.orch.max_y + self.orch.min_y) / 2))]
        self.landmarks.set_led(self.landmarks.leds[0], displaysConsts.GREEN)
        self.landmarks.set_led(self.landmarks.leds[1], displaysConsts.BLUE)

    def manage_events(self):
        if self.joystick.get_click():
            self.orch.stop_drone(self.current_drone)
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
                    elif mouse_event_obj[0] == 'led':
                        self.led = mouse_event_obj[1]
                    elif mouse_event_obj[0] == 'point':
                        self.orch.try_goto(self.current_drone, mouse_event_obj[1])
            elif event.type == pygame.KEYUP:
                self.manage_keyboard_event(event.key)

    def manage_keyboard_event(self, key):
        if key == pygame.K_SPACE:
            self.next_drone()
        elif key == pygame.K_u:
            self.orch.try_take_off(self.current_drone)
        elif key == pygame.K_l:
            self.orch.land(self.current_drone)
        elif key == pygame.K_s:
            self.orch.stop_drone(self.current_drone)
        elif key == pygame.K_r:
            if self.led:
                r, g, b = self.led.color
                new_r = 0 if r>0 else 255
                self.landmarks.set_led(self.led, (new_r, g, b))
        elif key == pygame.K_g:
            if self.led:
                r, g, b = self.led.color
                new_g = 0 if g > 0 else 255
                self.landmarks.set_led(self.led, (r, new_g, b))
        elif key == pygame.K_b:
            if self.led:
                r, g, b = self.led.color
                new_b = 0 if b > 0 else 255
                self.landmarks.set_led(self.led, (r, g, new_b))

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
