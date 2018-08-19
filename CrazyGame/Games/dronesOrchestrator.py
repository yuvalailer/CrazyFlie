import pygame

import drawer
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

class Board:
    def __init__(self, pos=DEFAULT_POS, size=DEFAULT_SIZE):
        self.drones = []
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        return

    def add_drone(self, drone):
        drone.display_surf = self.display_surf
        self.drones.append(drone)

    def render(self, draw_rect=False):
        if draw_rect:
            pygame.draw.rect(self.display_surf, drawer.BLACK, self.rect)
        for drone in self.drones:
           drone.render()

        pygame.display.update()