import pygame
from CrazyGame.pygameUtils import drawer
from CrazyGame.pygameUtils import displaysConsts
from CrazyGame import logger


cf_logger = logger.get_logger(__name__)

BOARD_BOUND_RECT = pygame.Rect(300, 50, drawer.MAIN_RECT.width-350, drawer.MAIN_RECT.height-100)


class DisplayBoard:
    def __init__(self, display_surf, orchestrator):
        self.display_surf = display_surf
        self._orch = orchestrator
        self.rect = self.get_display_board_rect()

    def get_display_board_rect(self):
        return BOARD_BOUND_RECT

    def render(self):
        pygame.draw.rect(self.display_surf, displaysConsts.WHITE, self.rect)

    def _render_drone(self, drone):
        pass