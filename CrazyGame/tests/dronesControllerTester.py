#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from fixSysPath import test_sys_path
test_sys_path()
from CrazyGame import logger
from CrazyGame.dronesController import DronesController

cf_logger = logger.get_logger(__name__) # debug(), info(), warning(), error(), exception(), critical()

drone_name = "crazyflie2"
def main():
	drones_controller = DronesController() # Optional variables: "ip", "port" and "buffer_size"
	if not drones_controller.connect(number_of_trials=5, time_between_trails=3):
		cf_logger.critical("Communication error")
		return
	drones_list = drones_controller.get_objects()
	cf_logger.info("drones_list: {}".format(drones_list))
	cf_logger.info("get_world_size: {}".format(drones_controller.get_world_size()))
	cf_logger.info("battery_status: {}".format(drones_controller.battery_status(drone_name)))
	drones_controller.take_off(drone_name)
	drones_controller.battery_status(drone_name)
	cf_logger.debug("get_object_position: {}".format(drones_controller.get_object_position(drone_name)))
	drones_controller.goto(drone_name, [1,1])
	cf_logger.debug("get_object_position: {}".format(drones_controller.get_object_position(drone_name)))
	drones_controller.land(drone_name)
	drones_controller.disconnect()

if __name__ == "__main__":
	cf_logger.info("######################################################")
	cf_logger.info("####                   Started                    ####")
	cf_logger.info("######################################################")
	main()
