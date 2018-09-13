import pygame
from pygameUtils import displayManager
from pygameUtils import displaysConsts
import logger
import logging
from shapely.geometry import Point

cf_logger = logger.get_logger(__name__, logging.INFO)

BOARD_BOUND_RECT = pygame.Rect(400, 50, displayManager.MAIN_RECT.width-450, displayManager.MAIN_RECT.height-100)


class DisplayBoard:
    def __init__(self, display_surf, orchestrator, landmark_manager):
        self.display_surf = display_surf
        self._orch = orchestrator
        self._landmark_manager = landmark_manager
        self.set_inner_rect()
        self.display = False
        self.led_radius = 8
        self.rect = self.get_display_board_rect()

    def set_inner_rect(self):
        ratio = self._orch.width/self._orch.height
        if ratio >= 1:
            width = BOARD_BOUND_RECT.width
            height = width // ratio

        else:
            height = BOARD_BOUND_RECT.height
            width = height * ratio

        self.inner_rect = pygame.Rect(0, 0, width, height)
        self.inner_rect.center = BOARD_BOUND_RECT.center
        self.convert_ratio = self.inner_rect.width / self._orch.width
        self.drone_radius = self.get_relative_drone_radius()

        min_x, min_y = self.translate_xy_real2board(Point(self._orch.min_x - self._orch.drone_radius,
                                                          self._orch.min_y - self._orch.drone_radius))
        max_x, max_y = self.translate_xy_real2board(Point(self._orch.max_x + self._orch.drone_radius,
                                                          self._orch.max_y + self._orch.drone_radius))
        self.working_rect = pygame.Rect(min_x, min_y, (max_x - min_x), (max_y - min_y))

    def get_display_board_rect(self):
        rect = pygame.Rect(0, 0, self.inner_rect.width + 2 * self.drone_radius, self.inner_rect.height + 2 * self.drone_radius)
        rect.center = self.inner_rect.center
        return rect

    def get_relative_drone_radius(self):
        ratio = self.inner_rect.width/self._orch.width
        return round(ratio * self._orch.drone_radius)

    def render(self):
        if not self.display:
            return
        cf_logger.debug("rendering board...")
        self._render_board()
        for drone in self._orch.drones:
            self._render_drone(drone)
        for led in self._landmark_manager.leds:
            self._render_led(led)
        for obstacle in self._landmark_manager.obstacles:
            self._render_obstacle(obstacle)

    def translate_xy_real2board(self, real_world_position):
        new_x = self.inner_rect.width - (real_world_position.x * self.convert_ratio)
        new_y = real_world_position.y * self.convert_ratio
        return round(self.inner_rect.left + new_x), round(self.inner_rect.top + new_y)

    def translate_xy_board2real(self, board_position):
        inner_board_x = board_position[0] - self.inner_rect.left
        inner_board_y = board_position[1] - self.inner_rect.top
        new_x = self._orch.width - (inner_board_x / self.convert_ratio)
        new_y = inner_board_y / self.convert_ratio
        return new_x, new_y

    def _render_board(self):
        pygame.draw.rect(self.display_surf, displaysConsts.BLACK, self.inner_rect)
        pygame.draw.rect(self.display_surf, displaysConsts.SMOKE, self.working_rect)

    def _render_drone(self, drone):
        drone.display_position = self.translate_xy_real2board(drone.position)
        width = 1 if drone.grounded else 0

        cf_logger.debug("drawing {} at ({})".format(drone.name, drone.display_position))
        if self.inside_bounds(drone.display_position):
            pygame.draw.circle(self.display_surf, drone.color, drone.display_position, self.drone_radius, width)

    def _render_led(self, led):
        led.display_position = self.translate_xy_real2board(led.position)
        if sum(led.color) != 0:
            pygame.draw.circle(self.display_surf, led.color, led.display_position, self.led_radius)
        else:
            pygame.draw.circle(self.display_surf, led.color, led.display_position, self.led_radius, 1)

    def _render_obstacle(self, obstacle):
        x, y = self.translate_xy_real2board(obstacle.position)
        # todo finish rendering

    def handle_mouse_event(self, pos):
        if self.inside_bounds(pos):
            for drone in self._orch.drones:
                if self.in_radius(pos, drone.display_position, self.drone_radius):
                    return 'drone', drone

            for led in self._landmark_manager.leds:
                if self.in_radius(pos, led.display_position, self.led_radius):
                    return 'led', led

            cf_logger.debug("clicked on {}".format(pos))
            return 'point', Point(self.translate_xy_board2real(pos))
        return None

    def in_radius(self, pos1, pos2, radius):
        in_x = pos1[0] - radius <= pos2[0] <= pos1[0] + radius
        in_y = pos1[1] - radius <= pos2[1] <= pos1[1] + radius
        return  in_x and in_y

    def inside_bounds(self, pos):
        bounds_x = self.inner_rect.left <= pos[0] <= self.inner_rect.right
        bounds_y = self.inner_rect.top <= pos[1] <= self.inner_rect.bottom
        if bounds_x and bounds_y:
            return True
        return False