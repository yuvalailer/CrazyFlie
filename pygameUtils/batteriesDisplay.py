import pygame
from pygameUtils import displaysConsts
import os
IMG = displaysConsts.BATTERY_DISPLAY_IMG
X_POSITION = 10
Y_POSITION = 20
POS = (X_POSITION, 320)
SIZE = (65, 45)


class BatteriesDisplay:
    def __init__(self, display_surf, orch, pos=POS, size=SIZE):
        self.orch = orch
        self.pos = pos
        self.size = size
        self.display = False
        self.display_surf = display_surf
        self.rect = []
        self.font = pygame.font.SysFont("arial", 15)
        self.step = (self.size[1] // (len(self.orch.drones) + 1)) - 25
        self.render()
        image = pygame.image.load(os.path.join(displaysConsts.PICTURE_DIRECTORY, IMG))
        self.background_img = pygame.transform.scale(image, self.size)

    def display_positions(self):
        num_drones = len(self.orch.drones)
        res = []
        for i in range(num_drones):
            position = (40 + i*85, Y_POSITION)
            temp = pygame.Rect(position[0], position[1], SIZE[0], SIZE[1])
            res.append(temp)
        self.rect = res




    def render(self):
        if not self.display:
            return

        self.orch.update_drones_battery()
        self.display_positions()
        for i, drone in enumerate(self.orch.drones):
            self.display_surf.blit(self.background_img, self.rect[i].topleft)
            temp = drone.name[-1]
            drone_name = 'Drone {}'.format(temp)
            text_surface = self.font.render(drone_name, False, displaysConsts.BLACK)
            position = (self.rect[i].centerx - text_surface.get_width() / 2,
                        (self.rect[i].top - text_surface.get_height() / 2) + 15)
            self.display_surf.blit(text_surface, position)

            text_surface = self.font.render(str(int(drone.battery_level)) + '%', False, displaysConsts.BLACK)
            position = (self.rect[i].centerx - text_surface.get_width() / 2,
                        (self.rect[i].top - text_surface.get_height() / 2) + 35)
            self.display_surf.blit(text_surface, position)









