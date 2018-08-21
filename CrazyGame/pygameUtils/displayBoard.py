import pygame
from CrazyGame.pygameUtils import drawer
from CrazyGame.pygameUtils import displaysConsts
from CrazyGame import landmarkManager
from CrazyGame import logger


cf_logger = logger.get_logger(__name__)

BOARD_BOUND_RECT = pygame.Rect(300, 50, drawer.MAIN_RECT.width-350, drawer.MAIN_RECT.height-100)


class DisplayBoard:
    def __init__(self, display_surf, orchestrator, landmark_manager):
        self.display_surf = display_surf
        self._orch = orchestrator
        self._landmark_manager = landmark_manager
        self.rect = self.get_display_board_rect()
        self.radius = self.get_relative_radius()
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
        rect = pygame.Rect(0, 0, self.rect.width - 2*self.radius, self.rect.height - 2*self.radius)
        rect.center = self.rect.center
        return rect

    def get_relative_radius(self):
        ratio = self.rect.width/self._orch.width
        return round(ratio * self._orch.drone_radius)

    def render(self):
        cf_logger.debug("rendering board...")
        pygame.draw.rect(self.display_surf, displaysConsts.WHITE, self.rect)
        for drone in self._orch.drones:
            self._render_drone(drone)
        for led in self._landmark_manager.leds:
            self._render_led(led)
        for obstacle in self._landmark_manager.obstacles:
            self._render_obstacle(obstacle)

    def translate_xy(self, real_world_position):
        ratio = self.inner_rect.width/self._orch.width
        new_x = self.inner_rect.width - (real_world_position.x * ratio)
        new_y = real_world_position.y * ratio
        return round(self.inner_rect.left + new_x), round(self.inner_rect.top + new_y)

    def _render_drone(self, drone):
        x, y = self.translate_xy(drone.position)
        width = 1 if drone.grounded else 0
        cf_logger.debug("drawing {} at ({}, {})".format(drone.name, x, y))
        pygame.draw.circle(self.display_surf, drone.color, (x, y), self.radius, width)

    def _render_led(self, led):
        x, y = self.translate_xy(led.position)
        # todo finish rendering

    def _render_obstacle(self, obstacle):
        x, y = self.translate_xy(obstacle.position)
        # todo finish rendering
