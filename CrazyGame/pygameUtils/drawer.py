import time
import pygame
import os
from CrazyGame import logger
from CrazyGame.pygameUtils import displaysConsts
from CrazyGame.pygameUtils import displayBoard

cf_logger = logger.get_logger(__name__)

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
        backgroundimage = pygame.image.load(os.path.join(displaysConsts.PICTURE_DIRECTORY, 'main_crazyflie.png'))
        self.display_surf.blit(backgroundimage, (0,0))
        self.buttons = []
        if update_display:
            pygame.display.update()

    def set_text_line(self, text='', update_display=True):
        pygame.draw.rect(self.display_surf, displaysConsts.WHITE, TEXT_LINE_RECT)

        textsurface = self.text_line_font.render(text, False, displaysConsts.BLACK)
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

    def check_mouse_event(self, event_type):
        pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.handle_mouse_event(event_type, pos):
                return 'button', button

        return self.board.handle_mouse_event(pos)

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
