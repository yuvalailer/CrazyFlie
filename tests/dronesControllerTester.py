#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from fixSysPath import test_sys_path
test_sys_path()
import logger
from Drivers.dronesController import DronesController
import sys
import math

cf_logger = logger.get_logger(__name__)  # debug(), info(), warning(), error(), exception(), critical()

EPSILON = 0.01
SLEEP_TIME = 0.5

cf_logger = logger.get_logger(__name__) # debug(), info(), warning(), error(), exception(), critical()

def main():
	drones_controller = DronesController() # Optional variables: "ip", "port" and "buffer_size"
	if not drones_controller.connect(number_of_trials=5, time_between_trails=3):
		cf_logger.critical("Communication error")
		return
	drones_list = drones_controller.get_drones()
	cf_logger.info("drones_list: {}".format(drones_list))
	cf_logger.info("get_world_size: {}".format(drones_controller.get_world_size()))
	cf_logger.info("battery_status: {}".format(drones_controller.battery_status("crazyflie2")))
	drones_controller.take_off("crazyflie2")
	cf_logger.debug("get_object_position: {}".format(drones_controller.get_object_position("crazyflie2")))
	drones_controller.goto("crazyflie2", [1,1])  # TODO -> goto without sleep?!
	cf_logger.debug("get_object_position: {}".format(drones_controller.get_object_position("crazyflie2")))
	drones_controller.land("crazyflie2")
	drones_controller.disconnect()

if __name__ == "__main__":
	cf_logger.info("######################################################")
	cf_logger.info("####                   Started                    ####")
	cf_logger.info("######################################################")
	main()
