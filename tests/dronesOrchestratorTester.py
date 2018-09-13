import logger
import time
from shapely.geometry import Point
from Drivers import dronesControllerSimulator
from Managers import dronesOrchestrator

cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start drones Orchestrator tester ####")


def initialize(controller):
    cf_logger.info("*** world size is - " + str(controller.get_world_size()))
    objects = controller.get_drones()
    cf_logger.info("**********************")
    cf_logger.info("*** The objects in the world are: {}".format(' '.join(objects)))
    cf_logger.info("**********************")


def get_drones_to_start_positions(world_x, world_y, orch, droneA, droneB, droneC, droneD):
    orch.try_take_off(droneA)
    orch.try_goto(droneA, Point(world_x-0.1, world_y/2+0.2))
    orch.land(droneA)
    orch.try_take_off(droneB)
    orch.try_goto(droneB, Point(world_x-0.1, world_y/2-0.2))
    orch.land(droneB)
    orch.try_take_off(droneC)
    orch.try_goto(droneC, Point(0+0.1, world_y/2+0.2))
    orch.land(droneC)
    orch.try_take_off(droneD)
    orch.try_goto(droneD, Point(0+0.1, world_y/2-0.2))
    orch.land(droneD)

def print_drone_positions(orch):
    cf_logger.info("**********************")
    cf_logger.info("*** DRONES POSITIONS ***")
    cf_logger.info("**********************")
    for drone in orch.drones:
        drone_alt = orch.get_drone_alt(drone)
        d = drone.name
        p = orch.update_drone_xy_pos(drone)
        k = drone_alt
        cf_logger.info(d + " - " + str(p) + " - " + str(k))


def move_collision_tests(orch, droneA, droneB):
    cf_logger.info("*** MOVE COLLISION TEST: ***")
    while True:
        cf_logger.info("{d} - {p} ".format(d=droneA.name, p=orch.update_drone_xy_pos(droneA)))
        cf_logger.info("{d} - {p} ".format(d=droneB.name, p=orch.update_drone_xy_pos(droneB)))
        if not orch.try_move_drone(droneA, (-1, 0)) or not \
                orch.try_move_drone(droneB, (1, 0)):
            break
        time.sleep(1)


def go_to_out_of_bounds_tests(orch, drone):
    cf_logger.info("*** GO TO OUT OF BOUNDS TEST ***")
    orch.try_goto(drone, Point(3, 0.1))


def move_out_of_bounds_tests(orch, drone):
    cf_logger.info("*** MOVE OUT OF BOUNDS TEST***")
    while orch.try_move_drone(drone, (1, 0)):
        time.sleep(1)


def takeoff_land_tests(orch, droneA, droneB):
    cf_logger.info("*** TESTING TAKE-OFF\LAND ISSUES ***")
    orch.try_take_off(droneB)
    orch.land(droneA)
    orch.land(droneB)


def grounded_tests(orch, droneA, droneB):
    cf_logger.info("*** TESTING GROUNDED DRONES ISSUES ***")
    orch.try_move_drone(droneB, (-1, 0))
    orch.try_goto(droneA, Point(1200, 400))


def collisions_takeoff_land_tests(orch, droneA, droneB):
    cf_logger.info("*** TESTING TAKE-OFF\LAND COLLISION ISSUES ***")
    orch.try_take_off(droneB)
    orch.land(droneA)


def main():
    controller = dronesControllerSimulator.DronesController()
    orch = dronesOrchestrator.DronesOrchestrator(controller)
    drone1, drone2, drone3, drone4 = tuple(orch.drones)

    initialize(controller)
    print_drone_positions(orch)
    get_drones_to_start_positions(controller.get_world_size()[0],
                                  controller.get_world_size()[1], orch, drone1, drone2,
                                  drone3, drone4)

    orch.try_take_off(drone2)
    orch.try_take_off(drone4)

    print_drone_positions(orch)
    move_collision_tests(orch, drone2, drone4)

    orch.try_take_off(drone1)

    go_to_out_of_bounds_tests(orch, drone1)
    print_drone_positions(orch)
    move_out_of_bounds_tests(orch, drone1)
    print_drone_positions(orch)
    takeoff_land_tests(orch, drone3, drone4)
    print_drone_positions(orch)
    grounded_tests(orch, drone3, drone4)
    orch.land(drone2)
    orch.try_goto(drone1, Point(1.5, 0.75))
    print_drone_positions(orch)
    collisions_takeoff_land_tests(orch, drone1, drone3)
    print_drone_positions(orch)

if __name__ == "__main__":
    main()

