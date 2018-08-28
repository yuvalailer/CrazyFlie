import time
from CrazyGame import logger
from CrazyGame.pygameUtils import displaysConsts
from shapely.geometry import Point
from shapely.geometry import LineString
from munch import Munch
import math
cf_logger = logger.get_logger(__name__)

DRONE_VELOCITY = 0.1
DRONE_STEP_SIZE = 0.1
DRONE_RADIUS = 0.1
TARGET_RADIUS = 0.05
MARGIN_X = 0.15
MARGIN_Y = 0.15

class DronesOrchestrator:
    def __init__(self, drones_controller):
        self.drones_controller = drones_controller
        self.size = self.drones_controller.get_world_size()

        cf_logger.info('world size is %s' % self.size)
        self.drone_radius = DRONE_RADIUS
        self.set_velocity(DRONE_VELOCITY)
        self.set_drone_step_size(DRONE_STEP_SIZE)

        self.drones = []
        for i, drone in enumerate(self.drones_controller.get_drones()):
            self.drones.append(Munch(name=drone,
                                     index=i,
                                     grounded=True,
                                     might_on_move=False,
                                     color=displaysConsts.BLACK))

        self.update_drones_positions()

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def min_x(self):
        return MARGIN_X + DRONE_RADIUS

    @property
    def max_x(self):
        return self.size[0] - MARGIN_X - DRONE_RADIUS

    @property
    def min_y(self):
        return MARGIN_Y + DRONE_RADIUS

    @property
    def max_y(self):
        return self.size[1] - MARGIN_Y - DRONE_RADIUS

    @property
    def drone_velocity(self):
        return self._drone_velocity

    def set_velocity(self, velocity):
        self._drone_velocity = velocity
        self.drones_controller.set_speed(velocity)

    @property
    def drone_step_size(self):
        return self._drone_step_size

    def set_drone_step_size(self, step_size):
        self._drone_step_size = step_size
        self.drones_controller.set_step_size(self._drone_step_size)

    def get_drone_pos(self, drone):
        return self.drones_controller.get_object_position(drone.name)

    def get_drone_alt(self, drone):
        return self.get_drone_pos(drone)[2]

    def update_drone_xy_pos(self, drone):
        pos = self.drones_controller.get_object_position(drone.name)
        drone.position = Point(pos[:2])
        return drone.position

    def update_drones_positions(self):
        for drone in self.drones:
            self.update_drone_xy_pos(drone)

    def stop_drone(self, drone):
        if drone.might_on_move:
            cf_logger.warning('stopping drone %s' % drone.name)
            self.drones_controller.move_drone(drone.name, [0, 0])
            drone.might_on_move = False

    def try_move_drone(self, drone, direction):
        if drone.grounded:
            cf_logger.warning('try to move grounded drone %s' % drone.name)
            return False
        target = self._get_drone_proximity_position(drone, direction)
        cf_logger.info('prox position is {} current position is {}'.format(target, drone.position))
        line = LineString([drone.position, target])

        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                temp_circle = temp_drone.position.buffer(self.drone_radius + DRONE_STEP_SIZE)
                inter = temp_circle.intersection(line)
                if inter.type == 'LineString':
                    cf_logger.warning('drone %s try to enter %s drone' % (drone.name, temp_drone.name))
                    cf_logger.info('other drone position {} radius {}'.format(temp_drone.position, math.sqrt(temp_circle.area/3.14)))
                    cf_logger.info('distance curr drone from other drone {}'.format(drone.position.distance(temp_drone.position)))
                    return False
        if not self.check_point_in_bounds(target, drone):
            return False
        cf_logger.debug('drone %s move in direction %s' % (drone.name, direction))
        self.drones_controller.move_drone(drone.name, direction)
        drone.might_on_move = True
        return True

    def try_take_off(self, drone, blocking=False):
        if not drone.grounded:
            cf_logger.warning('try to take off a flying drone %s' % drone.name)
            return False
        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                if drone.position.distance(temp_drone.position) < self.drone_radius*2:
                    cf_logger.warning('unable to take off %s because of %s' % (drone.name, temp_drone.name))
                    return False

        cf_logger.info('take off drone %s', drone.name)
        self.drones_controller.take_off(drone.name)

        if blocking:  #add timeout
            cf_logger.info('waiting to drone %s to take off', drone.name)
            while not self.drone_is_up(drone):
                time.sleep(0.2)

        drone.grounded = False

    def drone_is_up(self, drone):
        return self.get_drone_pos(drone)[2] > 0.45

    def drone_reach_position(self, drone, target):
        return self.update_drone_xy_pos(drone).distance(target) < TARGET_RADIUS

    def land(self, drone):
        if drone.grounded:
            cf_logger.warning('try to land a grounded drone %s' % drone.name)
            return
        cf_logger.info('landing drone %s' % drone.name)
        self.drones_controller.land(drone.name)
        drone.grounded = True

    def try_goto(self, drone, target):
        if drone.grounded:
            cf_logger.warning('goto failed - try to move grounded drone %s' % drone.name)
            return False
        line = LineString([drone.position, (target.x, target.y)])
        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                temp_circle = temp_drone.position.buffer(self.drone_radius * 2)
                inter = temp_circle.intersection(line)
                if inter.type == 'LineString':
                    cf_logger.warning('goto failed - drone %s try to enter %s drone' % (drone.name, temp_drone.name))
                    return False
        if not self.check_point_in_bounds(target, drone):
            return False

        cf_logger.warning('drone %s go to %s' % (drone.name, target))
        self.drones_controller.goto(drone.name, (target.x,target.y))
        drone.might_on_move = True
        return True

    def _get_drone_proximity_position(self, drone, direction):
        return Point(drone.position.x + direction[0] * self.drone_step_size,
                     drone.position.y + direction[1] * self.drone_step_size)

    def check_point_in_bounds(self, target, drone):
        if not (self.min_x <= target.x <= self.max_x):
            cf_logger.warning('drone %s is trying to move out of x bounds' % drone.name)
            return False
        if not (self.min_y <= target.y <= self.max_y):
            cf_logger.warning('drone %s is trying to move out of y bounds' % drone.name)
            return False
        return True

    def update_drones_battery(self):
        for drone in self.drones:
            drone.battery_level = self.drones_controller.battery_status(drone)

