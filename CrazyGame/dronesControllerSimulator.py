import logger
import socket
import time
import munch

cf_logger = logger.get_logger(__name__)

WORLD_X = 1000
WORLD_Y = 800

TAKEOFF_HEIGHT = 0.5
SPEED = 20

DRONES_NUM = 4


class DronesController:
    def __init__(self):
        self._world_size = [WORLD_X, WORLD_Y]
        self._objects = {}
        for i in range(1, DRONES_NUM+1):
            self._objects["crazyflie{}".format(i)] = munch.Munch(pos=(0, 0, 0), # TODO set starting pos
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
            return object.pos

        diff = time.time() - object.start_time
        if diff >= 1:
            object.on_the_go = False
            return object.pos

        return ( object.start_pos[0] + (object.pos[0] - object.start_pos[0]) * diff,
                 object.start_pos[1] + (object.pos[1] - object.start_pos[1]) * diff,
                  object.pos[2] )

    def move_drone(self, drone_name, direction_vector): # direction_vector = [x, y]
        drone = self._objects[drone_name]
        drone.start_pos = self.get_object_position(drone_name)
        cf_logger.info("start pos - {}".format(drone.start_pos))
        drone.start_time = time.time()
        drone.on_the_go = True
        drone.pos = (drone.start_pos[0] + direction_vector[0]*SPEED,
                     drone.start_pos[1] + direction_vector[1]*SPEED,
                     drone.start_pos[2])

    def goto(self, drone_name, pos): # pos = [x, y]
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
