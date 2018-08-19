import logger
import socket
import time
import munch

cf_logger = logger.get_logger(__name__)

WORLD_X = 800
WORLD_Y = 1000

TAKEOFF_HEIGHT = 0.5
SPEED = 20

DRONES_NUM = 4

class DronesController:
    def __init__(self):
        self.world_size = [WORLD_X, WORLD_Y]
        self.objects = {}
        for i in range(1, DRONES_NUM):
            self.objects["crazyflie{}".format(i)] = munch.Munch(pos=(0, 0, 0),
                                                                on_the_go=False,
                                                                start_pos=(0, 0, 0),
                                                                start_time=0.0)
        cf_logger.info("Demo drone controller connected")

    def get_world_size(self):
        return self.world_size

    def get_objects(self):
        return self.objects.keys()

    def get_object_position(self, object_name):
        if not self.objects[object_name].on_the_go:
            return self.objects[object_name].pos

        diff = time.time() - self.objects[object_name].start_time
        if diff >= 1:
            self.objects[object_name].on_the_go = False
            return self.objects[object_name].pos

        return ((self.objects[object_name].pos[0]-self.objects[object_name].start_pos[0])*diff,
                 (self.objects[object_name].pos[1]-self.objects[object_name].start_pos[1])*diff,
                self.objects[object_name].pos[2])

    def move_drone(self, drone_name, direction_vector): # direction_vector = [x, y]
        self.objects[drone_name].start_pos = self.get_object_position(drone_name)
        self.objects[drone_name].start_time = time.time()
        self.objects[drone_name].on_the_go = True
        self.objects[drone_name].pos = (self.objects[drone_name].start_pos[0] + direction_vector[0]*SPEED,
                                        self.objects[drone_name].start_pos[1] + direction_vector[1]*SPEED,
                                        self.objects[drone_name].start_pos[2])

    def goto(self, drone_name, pos): # pos = [x, y]
        self.objects[drone_name] = (pos[0],
                                    pos[1],
                                    self.objects[drone_name][2])

    def take_off(self, drone_name):
        self.objects[drone_name] = (self.objects[drone_name][0],
                                    self.objects[drone_name][1],
                                    TAKEOFF_HEIGHT)

    def land(self, drone_name):
        self.objects[drone_name] = (self.objects[drone_name][0],
                                    self.objects[drone_name][1],
                                    0)

    def battery_status(self, drone_name):
        return 0

    def disconnect(self):
        return