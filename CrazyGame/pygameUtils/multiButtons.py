import pygame
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)


class MultiButtons:
    def __init__(self, buttons, name):
        cf_logger.info('create multi button {}'.format(name))
        self.buttons = buttons
        self.pressed_button = None
        self.text = name

    def render(self):
        for button in self.buttons:
            button.render()

    def set_pressed(self, button, state):
        self.buttons[button].set_pressed(state)

    def select_button(self, button):
        if self.pressed_button:
            self.pressed_button.set_pressed(False)
        self.pressed_button = button

    def handle_mouse_event(self, event_type, mouse_location):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_location):
                if button == self.pressed_button:
                    break
                if event_type == pygame.MOUSEBUTTONDOWN:
                    button.set_pressed(True)
                elif event_type == pygame.MOUSEBUTTONUP and button.pressed:
                    self.select_button(button)
                self.render()
                pygame.display.update()
                break







