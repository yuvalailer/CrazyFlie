import pygame
import numpy as np


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
            return [0, 0]
        vector = np.array([ax, ay])
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector.tolist()

    def get_click(self):
        return self._click_func()


def _get_keyboard_click():
    return False # TODO -> NEVER TESTED - SHOULD WORK AS FOLLOWING:
    keys = pygame.key.get_pressed()
    return keys[pygame.K_KP_ENTER]


def _get_keyboard_direction():
    return 0, 0  # TODO -> NEVER TESTED - SHOULD WORK AS FOLLOWING:
    keys = pygame.key.get_pressed()
    print(keys)
    ax, ay = 0, 0
    if keys[pygame.K_UP]:
        ay += 1
    if keys[pygame.K_DOWN]:
        ay -= 1
    if keys[pygame.K_LEFT]:
        ax -= 1
    if keys[pygame.K_RIGHT]:
        ax += 1
    return ax, ay