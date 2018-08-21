import time
import munch
import numpy as np
import logger

cf_logger = logger.get_logger(__name__)

WORLD_X = 2.68
WORLD_Y = 1.92

TAKEOFF_HEIGHT = 0.5
VELOCITY = 0.1

DRONES_NUM = 4

NOISE_EXPECTATION_POS = 0
NOISE_VAR_POS = 10
NOISE_POS = False
NOISE_EXPECTATION_MOVE = 0
NOISE_VAR_MOVE = 10
NOISE_MOVE = False

NOISE_DIR = {'posnoise': (NOISE_EXPECTATION_POS, NOISE_VAR_POS, NOISE_POS),
             'movetonoise': (NOISE_EXPECTATION_MOVE, NOISE_VAR_MOVE, NOISE_MOVE)}

class DronesController:
    def __init__(self):
        self._world_size = [WORLD_X, WORLD_Y]
        self._objects = {}
        self.velocity = VELOCITY
        self.step = 0.1
        step = WORLD_Y/(DRONES_NUM+1)
        for i in range(0, DRONES_NUM):
            self._objects["crazyflie{}".format(i+1)] = munch.Munch(pos=(WORLD_X/2, step + i*step, 0),
                                                                 on_the_go=False,
                                                                 on_the_move=False,
                                                                 start_pos=(0, 0, 0),
                                                                 start_time=0.0)

    def connect(self):
        cf_logger.info("Demo drone controller connected")
        return True

    def connect(self):
        return True

    def get_world_size(self):
        return self._world_size

    def get_objects(self):
        return list(self._objects.keys())

    def set_speed(self, speed):
        self.velocity = speed

    def set_step_size(self, step):
        self.step = step

    def get_object_position(self, object_name):
        object = self._objects[object_name]
        diff = time.time() - object.start_time
        if object.on_the_move:
            if diff >= object.end_time:
                object.on_the_move = False
                return object.pos

            return ( object.start_pos[0] + (object.pos[0] - object.start_pos[0]) * diff + self.add_noise("posnoise"),
                     object.start_pos[1] + (object.pos[1] - object.start_pos[1]) * diff + self.add_noise("posnoise"),
                     object.pos[2])

        if object.on_the_go:
            x = object.pos[0] - object.start_pos[0]
            y = object.pos[1] - object.start_pos[1]
            c = (x**2+y**2)**0.5
            x_dir = x/c
            y_dir = y/c
            object.tmp = ( object.tmp[0] + x_dir * self.velocity + self.add_noise("posnoise"),
                           object.tmp[1] + y_dir * self.velocity + self.add_noise("posnoise"),
                           object.tmp[2])
            if object.pos[0]-self.velocity <= object.tmp[0] <= object.pos[0]+self.velocity and \
                   object.pos[1]-self.velocity <= object.tmp[1] <= object.pos[1]+self.velocity :
                cf_logger.info("reached destination")
                object.on_the_go = False
            return object.tmp

        for el in object.pos:
            el += self.add_noise("posnoise")
        return object.pos


    def move_drone(self, drone_name, direction_vector):  # direction_vector = [x, y]
        drone = self._objects[drone_name]
        drone.start_pos = self.get_object_position(drone_name)
        cf_logger.debug("start pos - {}".format(drone.start_pos))
        drone.start_time = time.time()
        drone.on_the_go = False
        drone.on_the_move = True
        drone.pos = (drone.start_pos[0] + direction_vector[0] * self.velocity + self.add_noise("movetonoise"),
                     drone.start_pos[1] + direction_vector[1] * self.velocity + self.add_noise("movetonoise"),
                     drone.start_pos[2])
        drone.end_time = ((direction_vector[0] * self.velocity)**2 + (direction_vector[1] * self.velocity)**2)**0.5 /self.velocity

    def goto(self, drone_name, pos):  # pos = [x, y]
        drone = self._objects[drone_name]
        drone.start_pos = self.get_object_position(drone_name)
        drone.tmp = drone.start_pos
        drone.on_the_move = False
        drone.on_the_go = True
        drone.start_time = time.time()
        drone.pos = (pos[0],
                      pos[1],
                      drone.pos[2])

    def take_off(self, drone_name):
        drone = self._objects[drone_name]
        drone.pos = (drone.pos[0],
                     drone.pos[1],
                     TAKEOFF_HEIGHT)

    def land(self, drone_name):
        drone = self._objects[drone_name]
        if not drone.on_the_move:
            drone.pos = (drone.pos[0],
                         drone.pos[1],
                         0)
        else:
            diff = time.time() - drone.start_time
            if diff >= 1:
                drone.on_the_move = False

            drone.pos = ( drone.start_pos[0] + (drone.pos[0] - drone.start_pos[0]) * diff + self.add_noise("posnoise"),
                          drone.start_pos[1] + (drone.pos[1] - drone.start_pos[1]) * diff + self.add_noise("posnoise"),
                          drone.pos[2])

    def battery_status(self, drone_name):
        return 0

    def disconnect(self):
        return

    def add_noise(self, noisesource):
        exp, var, use_noise = NOISE_DIR[noisesource]
        if not use_noise:
            return 0
        return np.random.normal(exp, var, 1)


