import time

from fixSysPath import test_sys_path

import logger

test_sys_path()
from Peripherals import dronesControllerSimulator

cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start controller sim tester ####")

def main():
    controller = dronesControllerSimulator.DronesController()
    cf_logger.info("*** world size is - " + str(controller.get_world_size()))

    objects = controller.get_objects()
    cf_logger.info("**********************")
    cf_logger.info("*** The objects in the world are: {}".format(' '.join(objects)))
    cf_logger.info("**********************")

    drones = []
    for object in objects:
        if object[0] == 'c':
            drones.append(object)

    for drone in drones:
        controller.take_off(drone)

    cf_logger.info("**********************")
    cf_logger.info("*** INITIAL POSITIONS ***")
    cf_logger.info("**********************")
    for drone in drones:
        cf_logger.info("{d} - {p}".format(d=drone, p=controller.get_object_position(drone)))

    cf_logger.info("\n**********************")
    cf_logger.info("*** DRONE MOVEMENT ***")
    cf_logger.info("**********************")
    drone = drones[0]
    controller.move_drone(drone, (0.6, 0.8))
    now = time.time()
    diff = 0
    while diff <= 1.5 :
        cf_logger.info("time - %.01f : %s" % (diff, controller.get_object_position(drone)))
        time.sleep(0.1)
        diff = time.time() - now
    #assert(controller.get_object_position(drone) == (12, 16, 0.5)),"Wrong dest!"

    cf_logger.info("**********************")
    cf_logger.info("*** INTERRUPTED MOVEMENT ***")
    cf_logger.info("**********************")
    drone = drones[1]
    controller.move_drone(drone, (0.6, 0.8))
    now = time.time()
    diff = 0
    epsilon = 0.01
    while diff <= 2.5 :
        if diff-epsilon <= 0.5 <= diff+epsilon:
            controller.move_drone(drone, (-0.6, 0.8))
        cf_logger.info("time - %.01f : %s" % (diff, controller.get_object_position(drone)))
        time.sleep(0.1)
        diff = time.time() - now
    #assert(controller.get_object_position(drone) == (12, 16, 0.5)),"Wrong dest!"

if __name__ == "__main__":
    main()
