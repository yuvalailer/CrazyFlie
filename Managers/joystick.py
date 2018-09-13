import pygame
import numpy as np
import logger

cp_logger = logger.get_logger(__name__)


class Joystick:
    def __init__(self, control_board_api):
        self._control_board_api = control_board_api
        if self._control_board_api:
            self._non_normalize_function = self._control_board_api.get_joystick_direction
            self._click_func = self._control_board_api.get_button
        else:
            self._non_normalize_function = _get_keyboard_direction
            self._click_func = _get_keyboard_click

    def get_normalize_direction(self):
        ax, ay = self._non_normalize_function()
        if ax == 0 and ay == 0:
            return None
        vector = np.array([ax, ay])
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector.tolist()

    def get_click(self):
        return self._click_func()


def _get_keyboard_click():
    keys = pygame.key.get_pressed()
    return keys[pygame.K_c]


def _get_keyboard_direction():
    keys = pygame.key.get_pressed()
    ax, ay = 0, 0
    if keys[pygame.K_UP]:
        ay -= 1
    if keys[pygame.K_DOWN]:
        ay += 1
    if keys[pygame.K_LEFT]:
        ax += 1
    if keys[pygame.K_RIGHT]:
        ax -= 1
    return ax, ay