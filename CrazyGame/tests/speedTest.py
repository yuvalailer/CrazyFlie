#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

## input:
#     - drone name: crazieflie5
#     - path to route.txt file:

from fixSysPath import test_sys_path

test_sys_path()
from CrazyGame import logger
from CrazyGame.Peripherals import dronesController
import sys
import math

cf_logger = logger.get_logger(__name__)  # debug(), info(), warning(), error(), exception(), critical()

EPSILON = 0.05
SLEEP_TIME = 2


def main():
    route_file = False  # Default
    drone_name = sys.argv[1]
    if len(sys.argv) > 2:
        route_file = open(sys.argv[2], "r")
    drones_controller = dronesController.DronesController()  # Optional variables: "ip", "port" and "buffer_size"
    if not drones_controller.connect(number_of_trials=5, time_between_trails=3):
        cf_logger.critical("Communication error")
        return
    drones_list = drones_controller.get_objects()
    cf_logger.info("drones_list: {}".format(drones_list))
    cf_logger.info("get_world_size: {}".format(drones_controller.get_world_size()))
    drones_controller.set_speed(0.2)
    drones_controller.set_step_size(0.2)
    cf_logger.info("battery_status: {}".format(drones_controller.battery_status(drone_name)))
    drones_controller.take_off(drone_name)
    time.sleep(2)
    drones_controller.battery_status(drone_name)
    cf_logger.debug("get_object_position: {}".format(drones_controller.get_object_position(drone_name)))
    if route_file:
        lines = route_file.readlines()
        points = [[float(n) for n in line.split(',')] for line in lines]
        first_point = True
        for point in points:
            cf_logger.info("[route test]\n on the way to point: %s" % point)
            if first_point:
                drones_controller.take_your_place(drone_name, point)
                first_point = False
            else:
                drones_controller.goto(drone_name, point)
            while True:
                pos = drones_controller.get_object_position(drone_name)
                dist = math.hypot(point[0] - pos[0], point[1] - pos[1])
                cf_logger.info('dist - %s' % dist)
                if dist <= EPSILON:
                    cf_logger.info("Got There!")
                    break
                time.sleep(0.2)
            time.sleep(SLEEP_TIME)
            cf_logger.info("\nFinished route\n")
        route_file.close()
    else:
        print("No route File")
    cf_logger.debug("get_object_position: {}".format(drones_controller.get_object_position(drone_name)))
    drones_controller.land(drone_name)
    drones_controller.disconnect()
    route_file.close()


if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()
