import pygame
from CrazyGame.pygameUtils import displayManager
from CrazyGame.pygameUtils import displaysConsts
from CrazyGame import logger
import logging
from shapely.geometry import Point

cf_logger = logger.get_logger(__name__, logging.INFO)

BOARD_BOUND_RECT = pygame.Rect(300, 50, displayManager.MAIN_RECT.width-350, displayManager.MAIN_RECT.height-100)


class DisplayBoard:
    def __init__(self, display_surf, orchestrator):
        self.display_surf = display_surf
        self._orch = orchestrator
        self.inner_rect = self.get_inner_rect()
        self.display = False
        self.convert_ratio = self.inner_rect.width/self._orch.width
        self.radius = self.get_relative_radius()
        self.rect = self.get_display_board_rect()

    def get_inner_rect(self):
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

    def get_display_board_rect(self):
        rect = pygame.Rect(0, 0, self.inner_rect.width + 2*self.radius, self.inner_rect.height + 2*self.radius)
        rect.center = self.inner_rect.center
        return rect

    def get_relative_radius(self):
        ratio = self.inner_rect.width/self._orch.width
        return round(ratio * self._orch.drone_radius)

    def render(self):
        if not self.display:
            return
        cf_logger.debug("rendering board...")
        pygame.draw.rect(self.display_surf, displaysConsts.WHITE, self.rect)
        for drone in self._orch.drones:
            self._render_drone(drone)

    def translate_xy_real2world(self, real_world_position):
        new_x = self.inner_rect.width - (real_world_position.x * self.convert_ratio)
        new_y = real_world_position.y * self.convert_ratio
        return round(self.inner_rect.left + new_x), round(self.inner_rect.top + new_y)

    def translate_xy_board2real(self, board_position):
        inner_board_x = board_position[0] - self.inner_rect.left
        inner_board_y = board_position[1] - self.inner_rect.top
        new_x = self._orch.width - (inner_board_x / self.convert_ratio)
        new_y = inner_board_y / self.convert_ratio
        return new_x, new_y

    def _render_drone(self, drone):
        drone.display_position = self.translate_xy_real2world(drone.position)
        width = 1 if drone.grounded else 0
        cf_logger.debug("drawing {} at ({})".format(drone.name, drone.display_position))
        if self.inside_bounds(drone.display_position):
            pygame.draw.circle(self.display_surf, drone.color, drone.display_position, self.radius, width)

    def handle_mouse_event(self, pos):
        if self.inside_bounds(pos):
            for drone in self._orch.drones:
                if self.pos_in_drone(pos, drone):
                    return 'drone', drone
            cf_logger.debug("clicked on {}".format(pos))
            return 'point', Point(self.translate_xy_board2real(pos))
        return None

    def pos_in_drone(self, pos, drone):
        return drone.display_position[0] - self.radius <= pos[0] <= drone.display_position[0] + self.radius and \
                drone.display_position[1] - self.radius <= pos[1] <= drone.display_position[1] + self.radius

    def inside_bounds(self, pos):
        bounds_x = self.inner_rect.left <= pos[0] <= self.inner_rect.right
        bounds_y = self.inner_rect.top <= pos[1] <= self.inner_rect.bottom
        if bounds_x and bounds_y:
            return True
        return False