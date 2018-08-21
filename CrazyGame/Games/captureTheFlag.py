import munch
import pygame
import time
import functools
from shapely.geometry import Point

from pygameUtils import displayManager
from pygameUtils import button
from pygameUtils import displaysConsts
from CrazyGame import logger
from CrazyGame import dronesOrchestrator

cf_logger = logger.get_logger(__name__)

BACK_BUTTON_SIZE = (100, 50)
BACK_BUTTON_POS = (50, displayManager.MAIN_RECT.height - 100)
TURN_TIME = 10
RENDER_RATE = 1/15


class CaptureTheFlag:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, 'back')

    def run(self):
        self.velocity = self.orch.drone_velocity
        self.step_size = self.orch.drone_step_size

        self.displayManager.reset_main_rect(update_display=False)
        self.displayManager.board.display = True
        self.add_buttons()
        self.displayManager.render()

        assert len(self.orch.drones) > 1, 'need at least two drones'
        self.set_players()

        self.quit = False
        self.running = True
        self.game_loop()

    def set_players(self):
        cf_logger.info('create players')
        self.players = [munch.Munch(name='your',
                                    drone=self.orch.drones[0],
                                    start_position=Point(0.25, 0.96),
                                    target=Point(2.43, 0.96),
                                    last_updated=0,
                                    prepare_to_turn=self.human_player_prepare_to_turn,
                                    manage_turn=self.human_player_manage_turn,
                                    winner_message='YOU ARE THE WINNER'),
                        munch.Munch(name='computer',
                                    drone=self.orch.drones[1],
                                    start_position=Point(2.43, 0.96),
                                    target=Point(0.25, 0.96),
                                    last_updated=0,
                                    prepare_to_turn=self.human_player_prepare_to_turn,
                                    manage_turn=self.human_player_manage_turn,
                                    winner_message='YOU LOSE, NOT TOO BAD')
                                    ]

        self.players[0].next_player = self.players[1]
        self.players[1].next_player = self.players[0]
        self.current_player = self.players[0]

    def game_loop(self):
        self.move_drones_to_start_position()
        cf_logger.info('start game')
        while self.running:
            cf_logger.info('run %s turn' % self.current_player.name)
            self.current_player.drone.color = displaysConsts.GREEN
            self.run_turn()
            self.current_player.drone.color = displaysConsts.BLACK
            self.orch.stop(self.current_player.drone)
            if self.player_reach_goal():
                cf_logger.info('%s turn arrive to goal' % self.current_player.name)
                break
            self.current_player = self.current_player.next_player
            self.displayManager.text_line.set_text('%s turn ended' % self.current_player.name)
            self.interactive_sleep(2)

        if not self.running:
            return
        self.displayManager.text_line.set_text(self.current_player.winner_message)
        self.land_drones()
        self.interactive_sleep(5)

    def run_turn(self):
        start_turn_time = time.time()
        self.current_player.prepare_to_turn()
        last_render_time = 0
        while self.running:
            current_time = time.time()
            turn_left_time = TURN_TIME - (current_time - start_turn_time)
            if turn_left_time < 0:
                break
            if current_time - last_render_time > RENDER_RATE:
                text = '%s - turn ends in %2f second' % (self.current_player.name, turn_left_time)
                self.displayManager.text_line.set_text(text, update_display=False)
                self.displayManager.render()
                last_render_time = time.time()
            self.current_player.manage_turn()
            self.manage_events()

    def land_drones(self):
        for player in self.players:
            self.orch.land(player.drone)

    def move_drones_to_start_position(self):
        for player in self.players:
            cf_logger.info("move %s to start position" % player.name)
            self.orch.try_take_off(player.drone)
            wait_func = functools.partial(self.orch.drone_is_up, player.drone)
            self.wait_to(wait_func, timeout=10)

            self.orch.try_goto(player.drone, player.start_position)
            wait_func = functools.partial(self.orch.drone_reach_position, player.drone, player.start_position)
            self.wait_to(wait_func, timeout=10)

            self.orch.land(player.drone)

        for player in self.players:
            self.orch.try_take_off(player.drone)
            wait_func = functools.partial(self.orch.drone_is_up, player.drone)
            self.wait_to(wait_func, timeout=10)

    def interactive_sleep(self, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.orch.update_drones_positions()
            self.displayManager.render()
            time.sleep(0.1)

    def wait_to(self, wait_func, timeout=60, sleep_time=0.2):
        start_time = time.time()
        while time.time() - start_time < timeout:
            cf_logger.info('wait for wait_func')
            if wait_func():
                break
            self.orch.update_drones_positions()
            self.displayManager.render()
            time.sleep(sleep_time)

    def player_reach_goal(self):
        return self.orch.drone_reach_position(self.current_player.drone, self.current_player.target)

    def human_player_prepare_to_turn(self):
        pass

    def human_player_manage_turn(self):
        if time.time() - self.current_player.last_updated > 0.05:
            self.orch.update_drones_positions()
            self.displayManager.render()
            joystick_dir = self.joystick.get_normalize_direction()
            self.orch.try_move_drone(self.current_player.drone, joystick_dir)
            self.current_player.last_updated = time.time()



    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.displayManager.handle_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_event_obj = self.displayManager.handle_mouse_event(event.type)
                if mouse_event_obj:
                    if mouse_event_obj[0] == 'button':
                        self.manage_button_click(mouse_event_obj[1])
                    elif mouse_event_obj[0] == 'drone':
                        self.next_drone(mouse_event_obj[1])
                    elif mouse_event_obj[0] == 'point':
                        self.orch.try_goto(self.current_drone, mouse_event_obj[1], blocking=True)
            elif event.type == pygame.KEYUP:
                self.manage_keyboard_event(event.key)

    def manage_keyboard_event(self, key):
        if key == pygame.K_e:
            self.running = False

    def manage_button_click(self, button):
        if button == self.back_button:
            self.running = False

    def add_buttons(self):
        self.displayManager.add_button(self.back_button)
