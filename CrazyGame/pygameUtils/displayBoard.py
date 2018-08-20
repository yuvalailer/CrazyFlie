import pygame
from CrazyGame.pygameUtils import drawer
from CrazyGame.pygameUtils import colors
from CrazyGame import logger


cf_logger = logger.get_logger(__name__)

BOARD_BOUND_RECT = pygame.Rect(300, 50, drawer.MAIN_RECT.width-350, drawer.MAIN_RECT.height-100)
RADIUS = 4


class DisplayBoard:
    def __init__(self, display_surf, orchestrator):
        self.display_surf = display_surf
        self._orch = orchestrator
        self.rect = self.get_display_board_rect()
        self.inner_rect = self.get_inner_rect()

    def get_display_board_rect(self):
        ratio = self._orch.width/self._orch.height
        if ratio >= 1:
            width = BOARD_BOUND_RECT.width
            height = width // ratio

        else:
            height = BOARD_BOUND_RECT.height
            width = height * ratio

        rect = pygame.Rect(0, 0, width, height)
        rect.center = BOARD_BOUND_RECT.center
        return rect

    def get_inner_rect(self):
        rect = pygame.Rect(0, 0, self.rect.width-2*RADIUS, self.rect.height-2*RADIUS)
        rect.center = self.rect.center
        return rect

    def render(self):
        cf_logger.info("rendering board...")
        pygame.draw.rect(self.display_surf, colors.WHITE, self.rect)
        for drone in self._orch.drones:
            self._render_drone(drone)

    def translate_xy(self, x, y):
        ratio = self.inner_rect.width/self._orch.width
        new_x = self.inner_rect.width - (x * ratio)
        new_y = y * ratio
        return new_x, new_y

    def _render_drone(self, drone):
        pos = self._orch.get_drone_pos(drone)
        new_pos = self.translate_xy(pos[0], pos[1])
        x = self.inner_rect.left + int(round(new_pos[0]))
        y = self.inner_rect.top + int(round(new_pos[1]))
        width = 0
        if drone.grounded:
            width = 1
        cf_logger.info("drawing {} at ({}, {})".format(drone.name, x, y))
        pygame.draw.circle(self.display_surf, drone.color, (x, y), 4, width)