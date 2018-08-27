import time
import munch
import numpy as np
import logger
import math

cf_logger = logger.get_logger(__name__)

WORLD_X = 2.46
WORLD_Y = 1.72

TAKEOFF_HEIGHT = 0.5
DEFAULT_VELOCITY = 0.1
DEFAULT_STEP_SIZE = 0.1
DRONES_NUM = 4

NOISE_EXPECTATION_POS = 0
NOISE_VAR_POS = 0.001
NOISE_POS = True
NOISE_EXPECTATION_MOVE = 0
NOISE_VAR_MOVE = 0.001
NOISE_MOVE = True

NOISE_DIR = {'posnoise': (NOISE_EXPECTATION_POS, NOISE_VAR_POS, NOISE_POS),
             'movetonoise': (NOISE_EXPECTATION_MOVE, NOISE_VAR_MOVE, NOISE_MOVE)}

class DronesController:
    def __init__(self):
        self._world_size = [WORLD_X, WORLD_Y]
        self._objects = {}
        self.velocity = DEFAULT_VELOCITY
        self.step_size = DEFAULT_STEP_SIZE
        step = WORLD_Y/(DRONES_NUM+1)
        for i in range(0, DRONES_NUM):
            self._objects["crazyflie{}".format(i+1)] = munch.Munch(pos=[WORLD_X/2, step + i*step],
                                                                   move=None,
                                                                   altitude=0)

    def connect(self, number_of_trials=5, time_between_trails=3):
        cf_logger.info("Demo drone controller connected")
        return True

    def get_world_size(self):
        return self._world_size

    def get_objects(self):
        return list(self._objects.keys())

    def set_speed(self, speed):
        self.velocity = speed

    def set_step_size(self, step):
        self.step_size = step

    def get_object_position(self, object_name):
        obj = self._objects[object_name]
        if obj.move:
            obj.pos = obj.move.get_position()
            if obj.move.move_end:
                obj.move = None
        return obj.pos + [obj.altitude]

    def move_drone(self, drone_name, direction_vector):
        cf_logger.debug("drone %s start new move" % drone_name)
        start_pos = self.get_object_position(drone_name)[:2]
        drone = self._objects[drone_name]
        if direction_vector == [0, 0]:
            drone.move = None
            drone.pos = start_pos
        else:
            target_pos = self.end_move_position(start_pos, direction_vector)
            drone.move = MoveManager(start_pos, target_pos, self.velocity)

    def end_move_position(self, start, direction):
        pos_x = start[0] + direction[0] * self.step_size + self.add_noise("movetonoise")
        pos_y = start[1] + direction[1] * self.step_size + self.add_noise("movetonoise")
        return [pos_x, pos_y]

    def goto(self, drone_name, pos):
        cf_logger.debug("drone %s start new goto" % drone_name)
        drone = self._objects[drone_name]
        start_pos = self.get_object_position(drone_name)[:2]
        target_pos = pos
        drone.move = MoveManager(start_pos, target_pos, self.velocity)

    def take_off(self, drone_name):
        drone = self._objects[drone_name]
        drone.altitude = 0.5

    def land(self, drone_name):
        drone = self._objects[drone_name]
        drone.pos = self.get_object_position(drone_name)[:2]
        drone.move = None
        drone.altitude = 0

    def battery_status(self, drone_name):
        return 0

    def disconnect(self):
        return

    def add_noise(self, noise_type):
        exp, var, use_noise = NOISE_DIR[noise_type]
        if not use_noise:
            return 0
        return np.random.normal(exp, var, 1)


class MoveManager:
    def __init__(self, start, target, velocity):
        self._start = start
        self._target = target
        self._velocity = velocity
        self._move_vector = (self._target[0] - self._start[0], self._target[1] - self._start[1])
        self._distance = math.hypot(self._move_vector[0], self._move_vector[1])
        self._start_time = time.time()
        self._total_time = self._distance / self._velocity
        self._end_time = self._start_time + self._total_time
        self._move_end = (self._distance == 0)

    @property
    def move_end(self):
        return self._move_end

    def get_position(self):
        if self.move_end:
            return list(self._target)

        current_time = time.time()
        if current_time > self._end_time:
            self._move_end = True
            return list(self._target)

        move_completed_ratio = (current_time - self._start_time) / self._total_time
        pos_x = self._start[0] + self._move_vector[0] * move_completed_ratio
        pos_y = self._start[1] + self._move_vector[1] * move_completed_ratio

        return [pos_x, pos_y]



