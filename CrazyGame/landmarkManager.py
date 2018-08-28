from munch import Munch
from CrazyGame.pygameUtils import displaysConsts
from shapely.geometry import Point

LED_RADIUS = 0.05


class LandmarkManager:
    def __init__(self, arduino_controller, drones_controller):
        self.drones_controller = drones_controller
        rigid_bodies = self.drones_controller.get_objects()
        self.real_leds = False
        self.leds = self._parse_leds(rigid_bodies)
        self.obstacles = self._parse_obstacles(rigid_bodies)
        self.arduino_cont = arduino_controller
        self.reset_leds()

    def _parse_leds(self, landmarks):
        leds = []
        for inx, obj in enumerate(landmarks):
            if obj.startswith('led'):
                self.real_leds = True
                leds.append(Munch(name=obj,
                                  number=inx,
                                  color=displaysConsts.BLACK,
                                  position=self.update_landmark_xy_position(obj)))

        return leds

    def _parse_obstacles(self, landmarks):
        obstacles = []
        for landmark in landmarks:
            if landmark.startswith('obstacle'):
                obstacles.append(Munch(name=landmark, color=displaysConsts.BLACK))
        return obstacles

    def initialize_leds(self, game_name):
        if not self.real_leds:
            if game_name == 'capture' or game_name == 'demo':
                self.leds = [Munch(name='led1', number=0, color=displaysConsts.GREEN, position=Point(2.30, 0.96)),
                            Munch(name='led2', number=1,color=displaysConsts.BLUE, position=Point(0.20, 0.96))]
            if game_name == 'grab':
                self.leds = [Munch(name='led1', number=0, color=displaysConsts.RED, position=Point(1.30, 0.96)),
                            Munch(name='led2', number=1,color=displaysConsts.RED, position=Point(0.90, 0.96))]

    def update_landmark_xy_position(self, landmark):
        pos = self.drones_controller.get_object_position(landmark.name)
        landmark.position = Point(pos[:2])
        return landmark.position

    def update_led_positions(self):
        for led in self.leds:
            self.update_landmark_xy_position(led)

    def update_obstacle_positions(self):
        for obstacle in self.obstacles:
            self.update_landmark_xy_position(obstacle)

    def reset_leds(self):
        for led in self.leds:
            self.set_led(led, displaysConsts.BLACK)
        if self.arduino_cont:
            self.arduino_cont.reset_leds()

    def set_led(self, led, color):
        led.color = color
        if self.arduino_cont:
            self.arduino_cont.set_led(led.number, *color)
