import time
from CrazyGame import logger
from CrazyGame.pygameUtils import displaysConsts
from shapely.geometry import Point
from shapely.geometry import LineString
from munch import Munch

cf_logger = logger.get_logger(__name__)

DRONE_VELOCITY = 0.1
DRONE_STEP_SIZE = 0.1
DRONE_DISTANCE_IN_TIME_OUT = DRONE_STEP_SIZE


class DronesOrchestrator:
    def __init__(self, drones_controller):
        self.drones_controller = drones_controller
        self.size = self.drones_controller.get_world_size()
        cf_logger.info('world size is %s'%self.size)
        self.drone_radius = 0.1
        self.drones_controller.set_speed(DRONE_VELOCITY)
        self._drone_velocity = DRONE_VELOCITY
        self._drone_step_size= DRONE_STEP_SIZE

        self.drones = []
        for i, drone in enumerate(self.drones_controller.get_objects()):
            self.drones.append(Munch(name=drone,
                                     index=i,
                                     grounded=True,
                                     in_move=False,
                                     color=displaysConsts.BLACK))

        self.update_drones_positions()

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def drone_velocity(self):
        return self._drone_velocity

    def set_velocity(self, velocity):
        self._drone_velocity = velocity
        self.drones_controller.set_speed(DRONE_VELOCITY)

    @property
    def drone_step_size(self):
        return self._drone_step_size

    def set_drone_step_size(self, drone_move_time_out):
        self._drone_step_size = drone_move_time_out

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

    def try_move_drone(self, drone, direction):
        if sum(direction) == 0:
            if drone.in_move:
                cf_logger.info('stop drone %s' % drone.name)
                self.drones_controller.move_drone(drone.name, (direction[0], direction[1]))
                drone.in_move = False
            return True
        if drone.grounded:
            cf_logger.warning('try to move grounded drone %s' % drone.name)
            return False
        target = self._get_drone_proximity_position(drone, direction)
        line = LineString([drone.position, target])

        for temp_drone in self.drones:
            if temp_drone != drone and not temp_drone.grounded:
                temp_circle = temp_drone.position.buffer(self.drone_radius*2)
                inter = temp_circle.intersection(line)
                if inter.type == 'LineString':
                    cf_logger.warning('drone %s try to enter %s drone' % (drone.name, temp_drone.name))
                    return False
        if not self.check_point_in_bounds(target, drone):
            return False
        self.drones_controller.move_drone(drone.name, direction)
        drone.in_move = True
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

        cf_logger.info('take off drone %s' % drone.name)
        self.drones_controller.take_off(drone.name)

        if blocking:
            while self.get_drone_alt(drone) < 0.3:
                time.sleep(0.2)

        drone.grounded = False

    def land(self, drone):
        if drone.grounded:
            cf_logger.warning('try to land a grounded drone %s' % drone.name)
            return
        self.drones_controller.land(drone.name)

        drone.grounded = True

    def try_goto(self, drone, target, blocking=False):
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

        if blocking:
            cf_logger.info('wait for %s to get the %s', drone.name, target)
            while self.update_drone_xy_pos(drone).distance(target) > 0.1:
                time.sleep(0.2)
        return True

    def _get_drone_proximity_position(self, drone, direction):
        return Point(drone.position.x + direction[0] * DRONE_DISTANCE_IN_TIME_OUT,
                     drone.position.y + direction[1] * DRONE_DISTANCE_IN_TIME_OUT)

    def check_point_in_bounds(self, target, drone):
        if not 0 <= target.x <= self.width:
            cf_logger.warning('drone %s is trying to move out of x bounds' % drone.name)
            return False
        if not 0 <= target.y <= self.height:
            cf_logger.warning('drone %s is trying to move out of y bounds' % drone.name)
            return False
        return True
