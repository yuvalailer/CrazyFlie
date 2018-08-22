import pygame

from pygameUtils import displayManager
from pygameUtils import button
from pygameUtils import displaysConsts

CIRCLE_RADIUS = 150
BACK_BUTTON_SIZE = (100, 50)
BACK_BUTTON_POS = (50, displayManager.MAIN_RECT.height - 100)


class JoystickDemo:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, '', 'back_button_unpressed.png', 'back_button_pressed.png')
        self.circle_position = (int(displayManager.MAIN_RECT.width / 2), int(displayManager.MAIN_RECT.height / 2))

    def run(self):
        self.displayManager.add_button(self.back_button)
        self.quit = False
        self.running = True
        last_joystick_dir = [-1, -1]
        while self.running:
            joystick_dir = self.joystick.get_normalize_direction()
            if joystick_dir != last_joystick_dir:
                self.draw_joystick_circle(joystick_dir)
            self.manage_events()

    def manage_events(self):
        if self.joystick.get_click():
            self.running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.displayManager.handle_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_event_obj = self.displayManager.handle_mouse_event(event.type)
                if mouse_event_obj and mouse_event_obj[0] == 'button':
                    button = mouse_event_obj[1]
                    if button == self.back_button:
                        self.running = False

    def draw_joystick_circle(self, joystick_dir):
        pygame.draw.circle(self.displayManager.display_surf, displaysConsts.BLUE, self.circle_position, CIRCLE_RADIUS)
        if joystick_dir:
            line_end_position = (self.circle_position[0] + 0.9*joystick_dir[0]*CIRCLE_RADIUS,
                                 self.circle_position[1] + 0.9*joystick_dir[1] * CIRCLE_RADIUS)
            pygame.draw.line(self.displayManager.display_surf, displaysConsts.GREEN, self.circle_position, line_end_position)
        else:
            pygame.draw.circle(self.displayManager.display_surf, displaysConsts.BLUE, self.circle_position, 3)
        pygame.display.update()
