# from fixSysPath import test_sys_path
import logging
import time
import sys
from CrazyGame import logger
from shapely.geometry import Point
from Games import pathFinder
from datetime import datetime
from CrazyGame import dronesOrchestrator
from Games import followPath
from Peripherals.dronesController import DronesController

# test_sys_path()
logger.set_default_logging_level(logging.INFO)
cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start silly player tester ####")


EPSILON = 0.05
SLEEP_TIME = 2


def main():

    drone_name = sys.argv[1]
    controller = DronesController()
    if not controller.connect(number_of_trials=5, time_between_trails=3):
        cf_logger.critical("Communication error")
        return
    orch = dronesOrchestrator.DronesOrchestrator(controller)
    drones_list = controller.get_objects()
    cf_logger.info("drones_list: {}".format(drones_list))
    # controller.set_speed(0.2)
    # controller.set_step_size(0.2)
    orch.try_take_off(orch.drones[0])
    time.sleep(2)
    cf_logger.debug("get_object_position: {}".format(controller.get_object_position(drone_name)))

    friend_drones = [Point(0, 0), Point(0.3, 0.3)]
    opponent_drones = [Point(30, 30), Point(10, 10)]
    target = Point(0.5, 0.5)

    start_time = datetime.now()
    path = pathFinder.silly_player_move(friend_drones, opponent_drones, target, 32)
    end_time = datetime.now()

    elapsed_time = end_time - start_time
    cf_logger.info('finding path took %f seconds'%elapsed_time.total_seconds())
    cf_logger.info('path length is ' + str(len(path)) + "points")

    cf_logger.info('go to first position: ' + str([path[0].x, path[0].y]))
    controller.take_your_place(drone_name, [path[0].x, path[0].y])

    cf_logger.info('start following the path')
    pf = followPath.Follower(path, orch.drones[0], orch)
    while not pf.is_completed():
        if not pf.follow_path():
            cf_logger.critical('PF failed to follow path')
            break
        # do things ...
        pos = orch.get_drone_pos(drone_name)
        cf_logger.info('path is:' + str([" " + str(point) for point in path]))
        cf_logger.info('drone location is: ' + str(pos))
        time.sleep(0.1)
    cf_logger.info('PF completed path')
    cf_logger.info('path is:' + str([" " + str(point) for point in path]))
    cf_logger.info('land')
    controller.land(drone_name)
    controller.disconnect()


if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()



