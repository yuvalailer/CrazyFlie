import munch
from munch import Munch
import pygame
import time
import random
import functools
from shapely.geometry import Point

from pygameUtils import displayManager
from pygameUtils import button
from pygameUtils import displaysConsts
import logger
from Games import followPath

cf_logger = logger.get_logger(__name__)

DIS_FROM_EDGE = 150
Y_POS = 300
BACK_BUTTON_SIZE = (360, 105)
CHOOSE_BUTTON_SIZE = (200, 130)
BACK_BUTTON_POS = (20, displayManager.MAIN_RECT.height - BACK_BUTTON_SIZE[1] - 15)
TURN_TIME = 10
RENDER_RATE = 1/15
MOUSE_LEFT_BUTTON = 1

LED_NUM = 4


class GrabAllFlags:
    def __init__(self):
        self.back_button = button.Button(BACK_BUTTON_POS, BACK_BUTTON_SIZE, '', 'back.png', 'back_pressed.png')
        self.quit = False
        self.running = True
        self.players = [munch.Munch(last_updated=0), munch.Munch(last_updated=0)]
        self.current_player = None

    def run(self):
        self.initialize()
        self.set_initialize_display()

        self.quit = False
        self.running = True
        self.game_loop()

    def initialize(self):
        if not self.landmarks.real_leds:
            self.set_virtual_leds()
        cf_logger.info('create players')
        self.drone = self.orch.drones[0]
        self.start_position = self.orch.update_drone_xy_pos(self.drone)
        self.players[0].color = displaysConsts.BLACK
        self.players[1].color = displaysConsts.BLUE
        for i in range(2):
            self.players[i].next_player = self.players[1-i]
            self.players[i].targets_left = self.get_targets()
            self.players[i].time = 0

        self.current_player = self.players[1]
        self.players[0].name = 'computer'
        self.players[1].name = 'your'

        if self.algolink:
            self.players[0].prepare_to_turn = self.computer_player_prepare_to_turn
        else:
            self.players[0].prepare_to_turn = self.computer_simulator_prepare_to_turn
        self.players[1].prepare_to_turn = self.human_player_prepare_to_turn

        self.players[0].manage_turn = self.computer_player_manage_turn
        self.players[1].manage_turn = self.human_player_manage_turn

        self.players[0].winner_message = 'YOU LOSE, TOO BAD, LOSER!!!'
        self.players[1].winner_message = 'YOU ARE THE WINNER'

    # Set the display for grab all flags mode
    def set_initialize_display(self):
        self.displayManager.reset_main_rect(True, 'ash.png')
        self.displayManager.text_line.set_text('grab all the flags')
        self.displayManager.board.display = True
        self.displayManager.batteriesDisplay.display = True
        self.add_buttons()
        self.displayManager.render(render_batteries=True)

    # If there are no real LEDs that can be captures by the cameras, we create them in the simulator manually
    def set_virtual_leds(self):
        self.landmarks.leds = self.generate_leds(LED_NUM)
        for led in self.landmarks.leds:
            self.landmarks.set_led(led, displaysConsts.RED)

    def generate_leds(self, led_num):
        leds = []
        for i in range(led_num):
            x = random.uniform(self.orch.min_x, self.orch.max_x)
            y = random.uniform(self.orch.min_y, self.orch.max_y)
            leds.append(Munch(name='led{}'.format(i),
                              number=i,
                              position=Point(x, y)))
        return leds

    def reset_leds(self):
        for led in self.landmarks.leds:
            led.visited = False
            self.landmarks.set_led(led, displaysConsts.RED)

    # Use LEDS as targets
    def get_targets(self):
        targets = [led for led in self.landmarks.leds]
        for target in targets:
            target.visited = False
        return targets

    def game_loop(self):
        self.orch.land(self.drone)
        cf_logger.info('start game')

        self.orch.try_take_off(self.drone)
        cf_logger.info('run %s turn' % self.current_player.name)
        self.displayManager.text_line.set_text('get ready for your turn!')
        self.interactive_sleep(2)
        running = True
        start_time = time.time()
        while running:
            current_time = time.time() - start_time
            self.displayManager.text_line.set_text('in {0:d}'.format(3-int(current_time)))
            if current_time >= 3:
                running = False
        for i in range(2):
            self.reset_leds()
            self.drone.color = self.current_player.color
            self.run_turn()
            self.orch.stop_drone(self.drone)
            self.move_drone_to_start_position()
            self.displayManager.text_line.set_text('%s turn ended' % self.current_player.name)
            self.current_player = self.current_player.next_player
            self.interactive_sleep(2)
            if not self.running:
                break

        if self.algolink:
                self.algolink.disconnect()

        if not self.running:
            self.orch.stop_drone(self.drone)
            return
        winner = self.calculate_winner()
        self.interactive_sleep(4)
        self.displayManager.text_line.set_text(winner.winner_message)
        self.orch.land(self.drone)
        self.interactive_sleep(3)

    def calculate_winner(self):
        text = "computer's time - {0:.2f}    |    your time - {1:.2f}".format(self.players[0].time, self.players[1].time)
        cf_logger.info(text)
        self.displayManager.text_line.set_text(text)
        return self.players[0] if (self.players[0].time < self.players[1].time) else self.players[1]

    def run_turn(self):
        start_turn_time = time.time()
        self.current_player.prepare_to_turn()
        last_render_time = 0
        while self.running:
            current_time = time.time()
            elapsed_time = current_time - start_turn_time
            if current_time - last_render_time > RENDER_RATE:
                text = '{0} - turn time {1:.2f} second'.format(self.current_player.name, elapsed_time)
                self.orch.update_drones_positions()
                self.displayManager.text_line.set_text(text, update_display=False)
                self.displayManager.render()
                last_render_time = time.time()
            self.current_player.manage_turn()
            self.manage_events()
            for led in self.current_player.targets_left:
                if not led.visited:
                    if self.player_reach_goal(led.position):
                        self.landmarks.set_led(led, displaysConsts.GREEN)
                        led.visited = True
            if not self.targets_left():
                self.current_player.time = elapsed_time
                break

    def targets_left(self):
        for led in self.current_player.targets_left:
            if not led.visited:
                return True
        return False

    def move_drone_to_start_position(self):
        cf_logger.info("move %s to start position" % self.drone.name)
        self.orch.try_take_off(self.drone)
        wait_func = functools.partial(self.orch.drone_is_up, self.drone)
        self.wait_to(wait_func, timeout=10)

        self.orch.try_goto(self.drone, self.start_position)
        wait_func = functools.partial(self.orch.drone_reach_position, self.drone, self.start_position)
        self.wait_to(wait_func, timeout=30)

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

    def player_reach_goal(self, goal):
        return self.orch.drone_reach_position(self.drone, goal)

    def computer_player_prepare_to_turn(self):
        sites = [led.position for led in self.landmarks.leds]
        path = self.algolink.capture_all_flags(self.start_position, sites, [], [])
        if not path:
            cf_logger.info('no path found')
            path = [self.orch.update_drone_xy_pos(self.drone)]*2
        self.current_player.follower = followPath.Follower(path, self.drone, self.orch)

    def computer_simulator_prepare_to_turn(self):
        path = [self.orch.update_drone_xy_pos(self.drone)]
        sites = [led.position for led in self.landmarks.leds]
        path.extend(sites)
        self.current_player.follower = followPath.Follower(path, self.drone, self.orch)

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
                self.orch.try_move_drone(self.drone, joystick_dir)
            else:
                self.orch.stop_drone(self.drone)
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
            self.running = False

    def add_buttons(self, choose=False):
        self.displayManager.add_button(self.back_button)