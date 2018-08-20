import pygame
from CrazyGame.pygameUtils import drawer
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

BOARD_BOUND_RECT = pygame.Rect(50,50, drawer.MAIN_RECT.width*0.7, drawer.MAIN_RECT.height*0.9)


class DisplayBoard:
    def __init__(self, display_surf, orchestrator):
        self._display_surf = display_surf
        self._orch = orchestrator
        self.rect = self.get_display_board_rect()

    def get_display_board_rect(self):
        return pygame.Rect(self._orch)

    def render(self, update_display=True):
        pass

    def _render_drone(self, drone):
        pass