import pygame
from pygameUtils import displaysConsts
import os
IMG = displaysConsts.BATTERY_DISPLAY_IMG
X_POSITION = 10
Y_POSITION = 20
POS = (X_POSITION, 320)
BATTERY_RECT_SIZE = (65, 45)


class BatteriesDisplay:
    def __init__(self, display_surf, orch, battery_rect_size=BATTERY_RECT_SIZE):
        self.orch = orch
        self.battery_rect_size = battery_rect_size
        self.display = False
        self.display_surf = display_surf
        self.set_batteries_positions()
        self.font = pygame.font.SysFont("arial", 15)
        self.step = (self.battery_rect_size[1] // (len(self.orch.drones) + 1)) - 25
        self.render()
        image = pygame.image.load(os.path.join(displaysConsts.PICTURE_DIRECTORY, IMG))
        self.background_img = pygame.transform.scale(image, self.battery_rect_size)

    def set_batteries_positions(self):
        num_drones = len(self.orch.drones)
        self.batteries_positions = []
        for i in range(num_drones):
            position = (40 + i*85, Y_POSITION)
            temp = pygame.Rect(position[0], position[1], self.battery_rect_size[0], self.battery_rect_size[1])
            self.batteries_positions.append(temp)

    def render(self):
        if not self.display:
            return

        self.orch.update_drones_battery()
        for drone, pos in zip(self.orch.drones, self.batteries_positions):
            self.display_surf.blit(self.background_img, pos.topleft)
            temp = drone.name[-1]
            drone_name = 'Drone {}'.format(temp)
            text_surface = self.font.render(drone_name, False, displaysConsts.BLACK)
            position = (pos.centerx - text_surface.get_width() / 2,
                        (pos.top - text_surface.get_height() / 2) + 15)
            self.display_surf.blit(text_surface, position)

            text_surface = self.font.render(str(int(drone.battery_level)) + '%', False, displaysConsts.BLACK)
            position = (pos.centerx - text_surface.get_width() / 2,
                        (pos.top - text_surface.get_height() / 2) + 35)
            self.display_surf.blit(text_surface, position)
