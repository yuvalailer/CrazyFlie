from munch import Munch
from CrazyGame.pygameUtils import displaysConsts
from shapely.geometry import Point


class LandmarkManager:
    def __init__(self, arduino_controller, drones_controller):
        self.drones_controller = drones_controller
        rigid_bodies = self.drones_controller.get_objects()
        self.leds = self._parse_leds(rigid_bodies)
        self.obstacles = self._parse_obstacles(rigid_bodies)
        self.arduino_cont = arduino_controller
        # todo handle the case of no landmarks in motive
        self.update_led_positions()
        self.update_obstacle_positions()
        self.reset_leds()

    def _parse_leds(self, landmarks):
        leds = [Munch(name=obj, color=displaysConsts.BLACK) for
                obj in landmarks if obj.startswith()]
        return leds

    def _parse_obstacles(self, landmarks):
        obstacles = []
        for landmark in landmarks:
            if landmark.startswith('obstacle'):
                obstacles.append(Munch(name=landmark, color=displaysConsts.BLACK))
        return obstacles

    def update_landmark_xy_position(self, landmark):
        pos = self.drones_controller.get_object_position(landmark.name)
        # todo update if can't find in the motive( if get_object_position doesn't find the name)
        landmark.position = Point(pos[:2])
        return landmark.position

    def update_led_positions(self):
        for led in self.leds:
            self.update_landmark_xy_position(led)

    def update_obstacle_positions(self):
        for obstacle in self.obstacles:
            self.update_landmark_xy_position(obstacle)

    def reset_leds(self):
        self.arduino_cont.reset_leds()  # todo handle the case of no arduino controller

    def set_led(self, led, r, g, b):
        self.arduino_cont.set_led(led, r, g, b) # todo handle the case of no arduino controller
