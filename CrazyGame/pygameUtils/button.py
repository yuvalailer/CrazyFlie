import pygame
import os
from pygameUtils import displaysConsts
from CrazyGame import logger
cf_logger = logger.get_logger(__name__)


UNPRESSED_BUTTON_IMAGE = 'button_unpressed.png'
PRESSED_BUTTON_IMAGE = 'button_pressed.png'


class Button:
    BUTTON_TEXT_COLOR = displaysConsts.WHITE

    def __init__(self, position, size, text, unpressed_image_name=UNPRESSED_BUTTON_IMAGE, pressed_image_name=PRESSED_BUTTON_IMAGE):
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.font = pygame.font.SysFont("arial", min(30, self.rect.height - 5))
        self.text = text
        self.size = size
        self.current_image = ''
        self.pressed = False
        self.text_surface = self.font.render(self.text, False, Button.BUTTON_TEXT_COLOR)
        self.text_position = (self.rect.centerx - self.text_surface.get_width() / 2,
                              self.rect.centery - self.text_surface.get_height() / 2)

        self.has_image = unpressed_image_name is not None
        self.unpressed_image_name = unpressed_image_name
        self.pressed_image_name = pressed_image_name
        self._set_images()
        self.set_pressed(False)
        self.current_color = (0, 0, 0)


    def render(self):
        if self.has_image:
            self.display_surf.blit(self.current_image, self.rect.topleft)
        else:
            pygame.draw.rect(self.display_surf, self.current_color, self.rect)

        self.display_surf.blit(self.text_surface, self.text_position)

    def set_pressed(self, state):
        self.pressed = state
        if self.pressed:
            self.current_color = displaysConsts.BLUE
            if self.has_image:
                self.current_image = self.pressed_image
        else:
            self.current_color = displaysConsts.GREEN
            if self.has_image:
                self.current_image = self.not_pressed_image

    def handle_mouse_event(self, event_type, mouse_location):
        if self.rect.collidepoint(*mouse_location):
            cf_logger.info('mouse event %s occurred on button %s'%(event_type, self.text))
            if event_type == pygame.MOUSEBUTTONDOWN:
                self.set_pressed(True)
            elif event_type == pygame.MOUSEBUTTONUP:
                if not self.pressed:
                    return False
                self.set_pressed(False)
            self.render()
            pygame.display.update()
            return True

        elif self.pressed:
            self.set_pressed(False)
            self.render()
            pygame.display.update()

        return False

    def _set_images(self):
        if self.has_image:
            button_unpressed_image = pygame.image.load(os.path.join(displaysConsts.PICTURE_DIRECTORY, self.unpressed_image_name))
            self.not_pressed_image = pygame.transform.scale(button_unpressed_image, self.size)
            button_pressed_image = pygame.image.load(os.path.join(displaysConsts.PICTURE_DIRECTORY, self.pressed_image_name))
            self.pressed_image = pygame.transform.scale(button_pressed_image, self.size)

    def is_pressed(self):
        return self.pressed

    def change_state(self):
        self.pressed = not self.pressed