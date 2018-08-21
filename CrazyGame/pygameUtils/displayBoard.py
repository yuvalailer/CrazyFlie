import pygame
from CrazyGame.pygameUtils import displayManager
from CrazyGame.pygameUtils import displaysConsts
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

BOARD_BOUND_RECT = pygame.Rect(300, 50, displayManager.MAIN_RECT.width - 350, displayManager.MAIN_RECT.height - 100)


class DisplayBoard:
    def __init__(self, display_surf, orchestrator):
        self.display_surf = display_surf
        self._orch = orchestrator
        self.rect = self.get_display_board_rect()
        self.convert_ratio = self.rect.width / self._orch.width
        cf_logger.info('convert ratio is %f' % self.convert_ratio)
        self.radius = self.get_relative_radius()
        self.inner_rect = self.get_inner_rect()
        self.display = False

    def get_display_board_rect(self):
        ratio = self._orch.width / self._orch.height
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
        rect = pygame.Rect(0, 0, self.rect.width - 2 * self.radius, self.rect.height - 2 * self.radius)
        rect.center = self.rect.center
        return rect

    def get_relative_radius(self):
        return round(self.convert_ratio * self._orch.drone_radius)

    def render(self):
        if not self.display:
            return
        cf_logger.debug("rendering board...")
        pygame.draw.rect(self.display_surf, displaysConsts.WHITE, self.rect)
        for drone in self._orch.drones:
            self._render_drone(drone)

    def _convert_world_to_display_xy(self, real_world_position):
        new_x = self.inner_rect.width - (real_world_position.x * self.convert_ratio)
        new_y = real_world_position.y * self.convert_ratio
        return round(self.inner_rect.left + new_x), round(self.inner_rect.top + new_y)

    def _render_drone(self, drone):
        drone.display_pos = self._convert_world_to_display_xy(drone.position)
        width = 1 if drone.grounded else 0
        cf_logger.debug("drawing {} at {}".format(drone.name, drone.display_pos))
        pygame.draw.circle(self.display_surf, drone.color, drone.display_pos, self.radius, width)

    def handle_mouse_event(self, mouse_location, event_type):
        if event_type != pygame.MOUSEBUTTONUP or self.rect.collidepoint(*mouse_location):
            return None

