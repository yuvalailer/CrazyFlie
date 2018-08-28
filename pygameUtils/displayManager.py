import pygame
import os
import logger
from pygameUtils import displaysConsts
from pygameUtils import displayBoard
from pygameUtils import batteriesDisplay

cf_logger = logger.get_logger(__name__)

WINDOW_RECT = (1280, 720)
MAIN_RECT = pygame.Rect(0, 0, WINDOW_RECT[0], WINDOW_RECT[1] - displaysConsts.TEXT_LINE_HEIGHT)


class DisplayManager:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.display_surf = pygame.display.set_mode(WINDOW_RECT, pygame.HWSURFACE)
        self.buttons = []
        self.multiButtons = []
        self.batteriesDisplay = None
        self.board = None
        pygame.display.set_caption('Crazy Game')
        self.reset_main_rect(update_display=False)
        self.text_line = TextLine(self.display_surf, 'Welcome To Crazy Game')
        self.default_picture = 'main_720p.png'
        pygame.display.update()

    def reset_main_rect(self, update_display=True, picture_name='main_720p.png'):
        background_image = pygame.image.load(os.path.join(displaysConsts.PICTURE_DIRECTORY, picture_name))
        self.display_surf.blit(background_image, (0, 0))
        self.buttons = []
        self.multiButtons = []
        if update_display:
            pygame.display.update()

    def add_button(self, button):
        button.display_surf = self.display_surf
        button.render()
        self.buttons.append(button)

    def add_multi_button(self, multi_button):
        for button in multi_button.buttons:
            button.display_surf = self.display_surf
            button.render()
        self.multiButtons.append(multi_button)

    def set_board(self, orch, landmark):
        self.board = displayBoard.DisplayBoard(self.display_surf, orch, landmark)

    def set_batteries_display(self, orch):
        self.batteriesDisplay = batteriesDisplay.BatteriesDisplay(self.display_surf, orch)

    def _render_buttons(self):
        for button in self.buttons:
            button.render()

        for multi_button in self.multiButtons:
            multi_button.render()

    def _check_buttons_mouse_event(self, pos, event_type):
        for button in self.buttons:
            if button.handle_mouse_event(event_type, pos):
                return 'button', button
        return None

    def _check_multi_buttons_mouse_event(self, pos, event_type):
        for mbutton in self.multiButtons:
            if mbutton.handle_mouse_event(event_type, pos):
                return 'mbutton', mbutton
        return None

    def _check_board_mouse_event(self, pos, event_type):
        if not self.board or not self.board.display:
            return None
        return self.board.handle_mouse_event(pos)

    def handle_mouse_event(self, event_type):
        handle_mouse_event_functions = [self._check_buttons_mouse_event,
                                        self._check_multi_buttons_mouse_event,
                                        self._check_board_mouse_event]
        pos = pygame.mouse.get_pos()
        for function in handle_mouse_event_functions:
            result = function(pos, event_type)
            if result:
                return result

        return None

    def _render_board(self):
        if self.board:
            self.board.render()

    def _render_batteries_display(self):
        if self.batteriesDisplay:
            self.batteriesDisplay.render()

    def render(self):
        self._render_buttons()
        self.text_line.render()
        self._render_board()
        self._render_batteries_display()

        pygame.display.update()


class TextLine:
    def __init__(self, display_surf, text=None):
        self.height = displaysConsts.TEXT_LINE_HEIGHT
        self.rect = pygame.Rect(0, WINDOW_RECT[1] - self.height, WINDOW_RECT[0], self.height)
        self._text = text
        self.display_surf = display_surf
        self.display = True
        self.font = pygame.font.SysFont("arial", 30)

    def render(self):
        if self.display:
            pygame.draw.rect(self.display_surf, displaysConsts.WHITE, self.rect)
            textsurface = self.font.render(self._text, False, displaysConsts.BLACK)
            text_pos = (self.rect.centerx - textsurface.get_width() / 2, self.rect.y + 10)
            self.display_surf.blit(textsurface, text_pos)

    def set_text(self, text, update_display=True):
        self._text = text
        self.display = True
        if update_display:
            self.render()
            pygame.display.update()