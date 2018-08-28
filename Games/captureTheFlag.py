import munch
from munch import Munch
import pygame
import time
import functools
from shapely.geometry import Point

from pygameUtils import displayManager, batteriesDisplay
from pygameUtils import button
from pygameUtils import multiLinesButton
from pygameUtils import displaysConsts
import logger
from Games import pathFinder
from Games import followPath

cf_logger = logger.get_logger(__name__)

DIS_FROM_EDGE = 150
Y_POS = 300
BACK_BUTTON_SIZE = (100, 50)
CHOOSE_BUTTON_SIZE = (200, 130)
BACK_BUTTON_POS = (50, displayManager.MAIN_RECT.height - 100)
COM_COM_BUTTON_POS = (DIS_FROM_EDGE, Y_POS)
COM_PLAYER_BUTTON_POS = (displayManager.MAIN_RECT.width - DIS_FROM_EDGE - CHOOSE_BUTTON_SIZE[0], Y_POS)
PLAYER_PLAYER_BUTTON_POS = ((displayManager.MAIN_RECT.width-CHOOSE_BUTTON_SIZE[0])/2, Y_POS)
TURN_TIME = 4
RENDER_RATE = 1/15
MOUSE_LEFT_BUTTON = 1
NUMBER_OF_PLAYERS = 2
CTF_IMAGE = 'capture_the_flag.png'


class CaptureTheFlag:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, '', 'back_button_unpressed.png', 'back_button_pressed.png')
        self.com_com_button = multiLinesButton.MultiLinesButton(COM_COM_BUTTON_POS, CHOOSE_BUTTON_SIZE, ['computer','vs','computer'])
        self.com_player_button = multiLinesButton.MultiLinesButton(COM_PLAYER_BUTTON_POS, CHOOSE_BUTTON_SIZE, ['player','vs','computer'])
        self.player_player_button = multiLinesButton.MultiLinesButton(PLAYER_PLAYER_BUTTON_POS, CHOOSE_BUTTON_SIZE, ['player','vs','player'])
        self.getting = True
        self.quit = False
        self.running = True
        self.players = [munch.Munch(last_updated=0), munch.Munch(last_updated=0)]
        self.current_player = None



    def run(self):
        self.velocity = self.orch.drone_velocity
        self.step_size = self.orch.drone_step_size
        assert len(self.orch.drones) > 1, 'need at least two drones'

        if not self.landmarks.real_leds:
            self.set_virtual_leds()
        self.initialize_players()

        self.choose_mode()
        if not self.running:
            return

        if self.current_mode == 'computerVsPlayer':
            self.displayManager.reset_main_rect(picture_name='computerVsPlayer.png')
        if self.current_mode == 'computerVsComputer':
            self.displayManager.reset_main_rect(picture_name='computerVsComputer.png')
        if self.current_mode == 'playerVsPlayer':
            self.displayManager.reset_main_rect(picture_name='playerVsPlayer.png')

        self.displayManager.text_line.set_text('capture the flag')
        self.displayManager.board.display = True
        self.displayManager.batteriesDisplay.display = True
        self.add_buttons()
        self.displayManager.render()

        self.quit = False
        self.running = True
        self.game_loop()
        self.displayManager.batteriesDisplay.display = False

    def set_virtual_leds(self):
        self.landmarks.leds = [Munch(name='led1', number=0,
                                     position=Point(self.orch.max_x - 0.5*self.orch.drone_radius,
                                                    (self.orch.max_y + self.orch.min_y) / 2)),
                               Munch(name='led2', number=1,
                                     position=Point(self.orch.min_x + 0.5*self.orch.drone_radius,
                                                    (self.orch.max_y + self.orch.min_y) / 2))]
        self.landmarks.set_led(self.landmarks.leds[0], displaysConsts.GREEN)
        self.landmarks.set_led(self.landmarks.leds[1], displaysConsts.BLUE)

    def allocate_players(self):
        self.players[0].drone = self.orch.drones[0]
        self.players[1].start_position = Point(self.orch.max_x - 1.5*self.orch.drone_radius,
                                               (self.orch.max_y + self.orch.min_y) / 2)
        self.players[1].drone = self.orch.drones[1]
        self.players[0].start_position = Point(self.orch.min_x + 1.5*self.orch.drone_radius,
                                               (self.orch.max_y + self.orch.min_y) / 2)
        self.players[0].color = displaysConsts.BLUE
        self.players[1].color = displaysConsts.GREEN

    def initialize_players(self):
        cf_logger.info('create players - {}'.format(len(self.players)))
        self.allocate_players()
        for i in range(2):
            self.players[i].led = self.landmarks.leds[i]
            self.players[i].target = self.landmarks.leds[i].position
            self.players[i].next_player = self.players[(i+1) % NUMBER_OF_PLAYERS]
            self.players[i].drone.color = displaysConsts.BLACK
            self.landmarks.set_led(self.players[i].led, self.players[i].color)

        self.current_player = self.players[1]

    def game_loop(self):
        for drone in self.orch.drones:
            self.orch.land(drone)
        self.move_drones_to_start_positions()
        cf_logger.info('start game')
        while self.running:
            cf_logger.info('run %s turn' % self.current_player.name)
            self.current_player.drone.color = self.current_player.color
            self.run_turn()
            self.orch.stop_drone(self.current_player.drone)
            if self.player_reach_goal():
                cf_logger.info('%s turn arrive to goal' % self.current_player.name)
                break
            self.current_player.drone.color = displaysConsts.BLACK
            self.displayManager.text_line.set_text('%s turn ended' % self.current_player.name)
            self.current_player = self.current_player.next_player
            self.interactive_sleep(2)

        if not self.running:
            self.orch.stop_drone(self.current_player.drone)
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
                self.orch.update_drones_positions()
                self.orch.update_drones_battery()
                self.displayManager.text_line.set_text(text, update_display=False)
                self.displayManager.render()
                last_render_time = time.time()
            self.current_player.manage_turn()
            self.manage_events()
        cf_logger.debug('player %s finished his movement at position: %s' % (self.current_player.name,
                                                                             self.orch.get_drone_pos(
                                                                                 self.current_player.drone)))

    def land_drones(self):
        for player in self.players:
            self.orch.land(player.drone)

    def move_drones_to_start_positions(self):
        for player in self.players:
            cf_logger.info("players - %d" % len(self.players))
            cf_logger.info("move %s to start position" % player.name)
            self.orch.try_take_off(player.drone)
            wait_func = functools.partial(self.orch.drone_is_up, player.drone)
            self.wait_to(wait_func, timeout=10)

            self.orch.try_goto(player.drone, player.start_position)
            wait_func = functools.partial(self.orch.drone_reach_position, player.drone, player.start_position)
            self.wait_to(wait_func, timeout=30)

            self.orch.land(player.drone)

        for player in self.players:
            self.orch.try_take_off(player.drone)
            wait_func = functools.partial(self.orch.drone_is_up, player.drone)
            self.wait_to(wait_func, timeout=10)

    def interactive_sleep(self, timeout):
        start_time = time.time()
        while self.running and time.time() - start_time < timeout:
            self.orch.update_drones_positions()
            self.displayManager.render()
            self.manage_events()
            time.sleep(0.1)

    def wait_to(self, wait_func, timeout=60, sleep_time=0.2):
        start_time = time.time()
        while self.running and time.time() - start_time < timeout:
            cf_logger.info('wait for wait_func')
            if wait_func():
                break
            self.orch.update_drones_positions()
            self.displayManager.render()
            self.manage_events()
            time.sleep(sleep_time)

    def player_reach_goal(self):
        return self.orch.drone_reach_position(self.current_player.drone, self.current_player.target)

    def computer_player_prepare_to_turn(self):
        friend_drones = [self.orch.update_drone_xy_pos(self.current_player.drone)]
        opponent_drones = [self.orch.update_drone_xy_pos(self.current_player.next_player.drone)]
        target = self.current_player.target
        cf_logger.critical('player %s current target is %s ' %(self.current_player.name, target))
        cf_logger.critical('player %s current position is: %s' %(self.current_player.name,
                                                                 self.orch.get_drone_pos(self.current_player.drone)))
        path = pathFinder.find_best_path(friend_drones, opponent_drones, target,
                                         self.orch.min_x, self.orch.max_x, self.orch.min_y, self.orch.max_y)
        if not path:
            cf_logger.info('no path found')
            path = [self.orch.update_drone_xy_pos(self.current_player.drone)]*2
        self.current_player.follower = followPath.Follower(path, self.current_player.drone, self.orch)

    def computer_player_manage_turn(self):
        if time.time() - self.current_player.last_updated > 0.1:
            self.current_player.follower.follow_path()
            self.current_player.last_updated = time.time()

    def human_player_prepare_to_turn(self):
        pass

    def human_player_manage_turn(self):
        if time.time() - self.current_player.last_updated > 0.05:
            joystick_dir = self.joystick.get_normalize_direction()
            if joystick_dir:
                self.orch.try_move_drone(self.current_player.drone, joystick_dir)
            else:
                self.orch.stop_drone(self.current_player.drone)
            self.current_player.last_updated = time.time()

    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                self.running = False
                self.getting = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT_BUTTON:
                self.displayManager.handle_mouse_event(event.type)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == MOUSE_LEFT_BUTTON:
                mouse_event_obj = self.displayManager.handle_mouse_event(event.type)
                if mouse_event_obj:
                    if mouse_event_obj[0] == 'button':
                        self.manage_button_click(mouse_event_obj[1])
            elif event.type == pygame.KEYUP:
                self.manage_keyboard_event(event.key)

    def manage_keyboard_event(self, key):
        if key == pygame.K_e:
            self.running = False

    def manage_button_click(self, button):
        if button == self.back_button:
            self.getting = False
            self.running = False
        if button == self.com_com_button:
            self.com_com_update()
            self.getting = False
        if button == self.com_player_button:
            self.com_player_update()
            self.getting = False
        if button == self.player_player_button:
            self.player_player_update()
            self.getting = False

    def com_com_update(self):
        self.current_mode = 'computerVsComputer'
        for i in range(2):
            self.players[i].name = 'computer {}'.format(i+1)
            self.players[i].prepare_to_turn = self.computer_player_prepare_to_turn
            self.players[i].manage_turn = self.computer_player_manage_turn
            self.players[i].winner_message = 'computer {} wins'.format(i+1)

    def com_player_update(self):
        self.current_mode = 'computerVsPlayer'
        self.players[0].name = 'computer'
        self.players[1].name = 'your'

        self.players[0].prepare_to_turn = self.computer_player_prepare_to_turn
        self.players[1].prepare_to_turn = self.human_player_prepare_to_turn

        self.players[0].manage_turn = self.computer_player_manage_turn
        self.players[1].manage_turn = self.human_player_manage_turn

        self.players[0].winner_message = 'YOU LOSE, TOO BAD, LOSER!!!'
        self.players[1].winner_message = 'YOU ARE THE WINNER'

    def player_player_update(self):
        self.current_mode = 'playerVsPlayer'
        for i in range(2):
            self.players[i].name = 'player {}'.format(i+1)
            self.players[i].prepare_to_turn = self.human_player_prepare_to_turn
            self.players[i].manage_turn = self.human_player_manage_turn
            self.players[i].winner_message = 'player {} wins'.format(i+1)

    def add_buttons(self, choose=False):
        self.displayManager.add_button(self.back_button)
        if choose:
            self.displayManager.add_button(self.com_com_button)
            self.displayManager.add_button(self.com_player_button)
            self.displayManager.add_button(self.player_player_button)

    def choose_mode(self):
        self.displayManager.reset_main_rect(picture_name=CTF_IMAGE)
        self.displayManager.text_line.set_text('Choose game mode')
        self.add_buttons(choose=True)
        self.displayManager.render()
        self.getting = True
        while self.getting:
            self.manage_events()
            time.sleep(0.1)
