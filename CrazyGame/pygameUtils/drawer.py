import time
import pygame
import os
from CrazyGame import logger
from CrazyGame.pygameUtils import colors
from CrazyGame.pygameUtils import displayBoard

cf_logger = logger.get_logger(__name__)

PICTURE_DIRECTORY = 'pictures'
WINDOW_RECT = (1000, 800)

TEXT_LINE_HEIGHT = 50
TEXT_LINE_RECT = pygame.Rect(0, WINDOW_RECT[1]-TEXT_LINE_HEIGHT,WINDOW_RECT[0],TEXT_LINE_HEIGHT)

MAIN_RECT = pygame.Rect(0, 0, WINDOW_RECT[0], WINDOW_RECT[1] - TEXT_LINE_HEIGHT)


class Drawer:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.display_surf = pygame.display.set_mode(WINDOW_RECT, pygame.HWSURFACE)
        self.text_line_font = pygame.font.SysFont("arial", 30)
        self.buttons = []
        self.board = None
        pygame.display.set_caption('Crazy Game')
        self.reset_main_rect(update_display=False)
        self.set_text_line('Welcome To Crazy Game', update_display=False)
        self.image_name = ''
        pygame.display.update()

    def reset_main_rect(self, update_display=True):
        backgroundimage = pygame.image.load(os.path.join(PICTURE_DIRECTORY, 'main_crazyflie.png'))
        self.display_surf.blit(backgroundimage, (0,0))
        self.buttons = []
        if update_display:
            pygame.display.update()

    def set_text_line(self, text='', update_display=True):
        pygame.draw.rect(self.display_surf, colors.WHITE, TEXT_LINE_RECT)

        textsurface = self.text_line_font.render(text, False, colors.BLACK)
        text_pos = (TEXT_LINE_RECT.centerx-textsurface.get_size()[0]/2, TEXT_LINE_RECT.y + 10)
        self.display_surf.blit(textsurface, text_pos)
        if update_display:
            pygame.display.update()

    def add_button(self, button):
        button.display_surf = self.display_surf
        button.render()
        self.buttons.append(button)

    def render_buttons(self, update_display=True):
        for button in self.buttons:
            button.render()

        if update_display:
            pygame.display.update()

    def check_buttons_mouse_event(self, event_type):
        pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.handle_mouse_event(event_type, pos):
                return button

        return None

    def set_board(self, orch):
        self.board = displayBoard.DisplayBoard(self.display_surf, orch)

    def render_board(self, update_display=False):
        if self.board:
            self.board.render()
            if update_display:
                pygame.display.update()

    def render(self):
        self.render_buttons()
        self.render_board()
        pygame.display.update()


class Button:
    BUTTON_TEXT_COLOR = colors.WHITE

    def __init__(self, position, size, text, unpressed_image_name=None , pressed_image_name=None):
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.font = pygame.font.SysFont("arial", min(30, self.rect.height - 5))
        self.text = text
        self.size = size
        self.text_surface = self.font.render(self.text, False, Button.BUTTON_TEXT_COLOR)
        self.text_position = (self.rect.centerx - self.text_surface.get_width() / 2,
                              self.rect.centery - self.text_surface.get_height() / 2)

        self.has_image = unpressed_image_name is not None
        self.unpressed_image_name = unpressed_image_name
        self.pressed_image_name = pressed_image_name
        self._set_images()
        self.set_pressed(False)


    def render(self):
        if self.has_image:
            self.display_surf.blit(self.current_image, self.rect.topleft)
        else:
            pygame.draw.rect(self.display_surf, self.current_color, self.rect)

        self.display_surf.blit(self.text_surface, self.text_position)

    def set_pressed(self, state):
        self.pressed = state
        if self.pressed:
            self.current_color = colors.BLUE
            if self.has_image:
                self.current_image = self.pressed_image
        else:
            self.current_color = colors.GREEN
            if self.has_image:
                self.current_image = self.not_pressed_image

    def handle_mouse_event(self, event_type, mouse_location): #add or not  * before mouse

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
            button_unpressed_image = pygame.image.load(os.path.join(PICTURE_DIRECTORY, self.unpressed_image_name))
            self.not_pressed_image = pygame.transform.scale(button_unpressed_image, self.size)
            button_pressed_image = pygame.image.load(os.path.join(PICTURE_DIRECTORY, self.pressed_image_name))
            self.pressed_image = pygame.transform.scale(button_pressed_image, self.size)