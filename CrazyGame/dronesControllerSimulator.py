import time
import munch
import numpy as np
import logger

cf_logger = logger.get_logger(__name__)

WORLD_X = 1000
WORLD_Y = 800

TAKEOFF_HEIGHT = 0.5
SPEED = 20

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
        for i in range(1, DRONES_NUM+1):
            player = (i-1)//2
            drone = (i-1)%2
            self._objects["crazyflie{}".format(i)] = munch.Munch(pos=(0 + WORLD_X*player, WORLD_Y/2 + drone*50, 0),
                                                                 on_the_go=False,
                                                                 start_pos=(0, 0, 0),
                                                                 start_time=0.0)
        cf_logger.info("Demo drone controller connected")

    def get_world_size(self):
        return self._world_size

    def get_objects(self):
        return list(self._objects.keys())

    def get_object_position(self, object_name):
        object = self._objects[object_name]
        if not object.on_the_go:
            for el in object.pos:
                el += self.add_noise("posnoise")
            return object.pos

        diff = time.time() - object.start_time
        if diff >= 1:
            object.on_the_go = False
            return object.pos

        return ( object.start_pos[0] + (object.pos[0] - object.start_pos[0]) * diff + self.add_noise("posnoise"),
                 object.start_pos[1] + (object.pos[1] - object.start_pos[1]) * diff + self.add_noise("posnoise"),
                  object.pos[2])

    def move_drone(self, drone_name, direction_vector):  # direction_vector = [x, y]
        drone = self._objects[drone_name]
        drone.start_pos = self.get_object_position(drone_name)
        cf_logger.debug("start pos - {}".format(drone.start_pos))
        drone.start_time = time.time()
        drone.on_the_go = True
        drone.pos = (drone.start_pos[0] + direction_vector[0] * SPEED + self.add_noise("movetonoise"),
                     drone.start_pos[1] + direction_vector[1] * SPEED + self.add_noise("movetonoise"),
                     drone.start_pos[2])

    def goto(self, drone_name, pos):  # pos = [x, y]
        self._objects[drone_name].pos = (pos[0],
                                         pos[1],
                                         self._objects[drone_name].pos[2])

    def take_off(self, drone_name):
        drone = self._objects[drone_name]
        drone.pos = (drone.pos[0],
                     drone.pos[1],
                     TAKEOFF_HEIGHT)

    def land(self, drone_name):
        drone = self._objects[drone_name]
        drone.pos = (drone.pos[0],
                     drone.pos[1],
                     0)

    def battery_status(self, drone_name):
        return 0

    def disconnect(self):
        return

    def add_noise(self, noisesource):
        exp, var, use_noise = NOISE_DIR[noisesource]
        if not use_noise:
            return 0
        return np.random.normal(exp, var, 1)


