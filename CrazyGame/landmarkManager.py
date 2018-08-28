from munch import Munch
from CrazyGame.pygameUtils import displaysConsts
from shapely.geometry import Point

LED_RADIUS = 0.05


class LandmarkManager:
    def __init__(self, arduino_controller, drones_controller):
        self.drones_controller = drones_controller
        rigid_bodies = self.drones_controller.get_leds()
        self.real_leds = False
        self.leds = self._parse_leds(rigid_bodies)
        self.obstacles = self._parse_obstacles(rigid_bodies)
        self.arduino_cont = arduino_controller
        self.reset_leds()

    def _parse_leds(self, landmarks):
        leds = []
        for inx, obj in enumerate(landmarks):
            if obj.startswith('led'):
                leds.append(Munch(name=obj,
                                  number=inx,
                                  color=displaysConsts.BLACK,
                                  position=self.update_landmark_xy_position(obj)))
        self.real_leds = len(leds) > 0
        return leds

    def _parse_obstacles(self, landmarks):
        obstacles = []
        for landmark in landmarks:
            if landmark.startswith('obstacle'):
                obstacles.append(Munch(name=landmark, color=displaysConsts.BLACK))
        return obstacles

    def update_landmark_xy_position(self, landmark):
        position = Point(self.drones_controller.get_object_position(landmark)[:2])
        return position

    def update_led_positions(self):
        for led in self.leds:
            self.update_landmark_xy_position(led.name)

    def update_obstacle_positions(self):
        for obstacle in self.obstacles:
            self.update_landmark_xy_position(obstacle.name)

    def reset_leds(self):
        for led in self.leds:
            self.set_led(led, displaysConsts.BLACK)
        if self.arduino_cont:
            self.arduino_cont.reset_leds()

    def set_led(self, led, color):
        led.color = color
        if self.arduino_cont:
            self.arduino_cont.set_led(led.number, *color)
