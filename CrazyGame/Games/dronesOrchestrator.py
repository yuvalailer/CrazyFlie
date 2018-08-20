import time
from CrazyGame import logger
from CrazyGame.pygameUtils import colors
from shapely.geometry import Point
from shapely.geometry import LineString
from munch import Munch

cf_logger = logger.get_logger(__name__)

DRONE_VELOCITY = 20
DRONE_MOVE_TIME_OUT = 1
DRONE_DISTANCE_IN_TIME_OUT = DRONE_VELOCITY * DRONE_MOVE_TIME_OUT
DRONE_RADIUS = 5


class DronesOrchestrator:
    def __init__(self, drone_controller):
        self.drone_controller = drone_controller
        self.size = drone_controller.size
        self.drones = []

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def add_drones(self, drones):
        for drone in drones:
            self.drones.append(Munch(name=drone, grounded=True, color=colors.BLACK))

    def try_move_drone(self, drone, direction):  # TODO -> consider board limits
        if drone.grounded:
            cf_logger.warning('try to move grounded drone %s' % drone.name)
            return False
        target = self._get_drone_approximity_position(drone, direction)
        line = LineString([drone, target])
        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                temp_circle = temp_drone.position.buffer(DRONE_RADIUS*2)
                inter = temp_circle.intersection(line)
                if inter.type == 'LineString':
                    cf_logger.warning('drone %s try to enter %s drone' % (drone.name, temp_drone.name))
                    return False
        if not self.check_if_leaving_bounds(target, drone):
            return False
        self.drones_controller.move_drone(drone.name, direction)
        return True

    def try_take_off(self, drone, blocking=False):
        if not drone.grounded:
            cf_logger.warning('try to take off a flying drone %s' % drone.name)
            return False
        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                if drone.position.distance(temp_drone.position):
                    cf_logger.warning('unable to take off %s because of %s' % (drone.name, temp_drone.name))
                    return False

        self.drones_controller.take_off(drone.name)

        if blocking:
            while self.drones.get_object_position(drone.name)[2] < 0.3:
                time.sleep(0.2)

        drone.grounded = False

    def land(self, drone, blocking=False):
        if not drone.up:
            cf_logger.warning('try to land a grounded drone %s' % drone.name)
            return
        self.drones_controller.land(drone.name)
        if blocking:
            while self.drones.get_object_position(drone.name)[2] > 0.2:
                time.sleep(0.2)

        drone.grounded = True

    def try_goto(self, drone, target, blocking=False):
        if drone.grounded:
            cf_logger.warning('try to move grounded drone %s' % drone.name)
            return False
        line = LineString([drone.position, target])
        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                temp_circle = temp_drone.position.buffer(DRONE_RADIUS*2)
                inter = temp_circle.intersection(line)
                if inter.type == 'LineString':
                    cf_logger.warning('drone %s try to enter %s drone' % (drone.name, temp_drone.name))
                    return False
        if not self.check_if_leaving_bounds(target, drone):
            return False

        self.drones_controller.goto(drone.name, target)

        if blocking:
            while Point(self.drones.get_object_position(drone.name)[:2]).distance(target) > 10:
                time.sleep(0.2)
        return True

    def _get_drone_approximity_position(self, drone, direction):
        return Point(drone.position.x + direction[0] * DRONE_DISTANCE_IN_TIME_OUT,
                     drone.position.y + direction[1] * DRONE_DISTANCE_IN_TIME_OUT)

    def check_if_leaving_bounds(self, target, drone):
        if target[0] > self.width() or target[0] < 0:
            cf_logger.warning('drone %s is trying to move out of width/x bounds' % (drone.name))
            return False
        if target[1] > self.height() or target[1] < 0:
            cf_logger.warning('drone %s is trying to move out of height/y bounds' % (drone.name))
            return False