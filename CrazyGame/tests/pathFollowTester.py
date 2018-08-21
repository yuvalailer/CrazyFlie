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
from Peripherals import dronesControllerSimulator

# test_sys_path()
logger.set_default_logging_level(logging.INFO)
cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start silly player tester ####")


EPSILON = 0.05
SLEEP_TIME = 2

def setup_orch():
    controller = dronesControllerSimulator.DronesController()
    if not controller.connect(number_of_trials=5, time_between_trails=3):
        raise Exception("Communication error")
    orch = dronesOrchestrator.DronesOrchestrator(controller)
    return orch

def find_path(friend_drones, opponent_drones, target):
    start_time = datetime.now()
    path = pathFinder.find_best_path(friend_drones, opponent_drones, target, 100)
    end_time = datetime.now()

    elapsed_time = end_time - start_time
    cf_logger.info('finding path took %f seconds' % elapsed_time.total_seconds())
    cf_logger.info('path is: [%s]' % (" ".join([str(point) for point in path])))
    cf_logger.info('path length is ' + str(len(path)) + "points")

    cf_logger.info('start following the path')
    return path

def main():
    orch = setup_orch()
    drone = orch.drones[0]
    orch.try_take_off(drone, blocking=True)
    target = Point(0.5, 0.5)
    path = find_path([orch.update_drone_xy_pos(orch.drones[0])], [orch.update_drone_xy_pos(orch.drones[1])], target)

    pf = followPath.Follower(path, orch.drones[0], orch)
    while not pf.completed:
        if not pf.follow_path():
            cf_logger.critical('PF failed to follow path')
            break
        # do things ...
        pos = orch.get_drone_pos(drone)
        cf_logger.info('drone location is: %s' % pos)
        time.sleep(0.1)

    cf_logger.info('PF completed path')
    cf_logger.info('land')
    orch.land(drone)

if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()



