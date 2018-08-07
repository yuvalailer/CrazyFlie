import pygame
import numpy as np

pygame.init()

class Joystick():
    def __init__(self, controlBoardAPI=None):
        self._controlBoardAPI = controlBoardAPI
        if self._controlBoardAPI:
            self._non_normalize_function = self._controlBoardAPI.get_joystick_direction
        else:
            self._non_normalize_function = self._get_keyboard_direction

    def get_normalize_direction(self):
        ax, ay = self._non_normalize_function()
        vector = np.array([ax, ay])
        normalized_vector = vector/ np.linalg.norm(vector)
        return normalized_vector.tolist()

    def _get_keyboard_direction(self):
        return 0, 0 #TODO -> NEVER TESTED - SHOUD WORK AS FOLLOWING:
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
       # print('%d %d' %(ax, ay))
        return ax, ay