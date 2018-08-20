import pygame
import time

from pygameUtils import drawer

CIRCLE_RADIUS = 150
BACK_BUTTON_SIZE = (100, 50)
BACK_BUTTON_POS = (50, drawer.MAIN_RECT.height / 2 - BACK_BUTTON_SIZE[1] / 2)


class DronesControlDemo:
    def __init__(self):
        self.back_button = drawer.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, 'back')
        self.circle_position = (int(drawer.MAIN_RECT.width / 2), int(drawer.MAIN_RECT.height / 2))

    def run(self):
        self.drawer.reset_main_rect(update_display=False)
        self.drawer.add_button(self.back_button)
        self.drawer.render()

        while True:
            joystick_dir = self.joystick.get_normalize_direction()
            event_result = self.manage_events()
            if event_result != 'continue':
                return event_result

    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawer.check_buttons_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = self.drawer.check_buttons_mouse_event(event.type)
                if button == self.back_button:
                    return 'game ended'
        return 'continue'

    def draw_joystick_circle(self, joystick_dir):
        pygame.draw.circle(self.drawer.display_surf, drawer.BLUE, self.circle_position, CIRCLE_RADIUS)
        if joystick_dir != [0, 0]:
            line_end_position = (self.circle_position[0] + 0.9*joystick_dir[0]*CIRCLE_RADIUS,
                                 self.circle_position[1] + 0.9*joystick_dir[1] * CIRCLE_RADIUS)
            pygame.draw.line(self.drawer.display_surf, drawer.GREEN, self.circle_position, line_end_position)
        else:
            pygame.draw.circle(self.drawer.display_surf, drawer.BLUE, self.circle_position, 3)
        pygame.display.update()
