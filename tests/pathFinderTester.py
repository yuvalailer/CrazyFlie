from fixSysPath import test_sys_path
test_sys_path()
import logging
import logger
logger.set_default_logging_level(logging.INFO)
cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start path finder tester ####")
from shapely.geometry import Point
import matplotlib.pyplot as plt
from Games import pathFinder
from datetime import datetime
from Drivers import dronesControllerSimulator
from Managers import dronesOrchestrator


def plot_player(ax, p, r, c):
    circle =  plt.Circle((p.x, p.y), r, color=c, fill=False)
    ax.add_artist(circle)

friend_drones = [Point(1.2658436973210652, 0.7454362221736588)]
opponent_drones = [Point(0.4023771151172205, 0.9766529476891986)]
target = Point(2.3, 0.96)

start_time = datetime.now()
drones_simulator = dronesControllerSimulator.DronesController()
orch = dronesOrchestrator.DronesOrchestrator(drones_simulator)
world_size = drones_simulator.get_world_size()
path = pathFinder.find_best_path(friend_drones, opponent_drones, target,
                                 orch.min_x, orch.max_x, orch.min_y, orch.max_y)
end_time = datetime.now()

elapsed_time = end_time - start_time
cf_logger.info('finding path took %f seconds'%elapsed_time.total_seconds())

plt.figure(figsize=(7,7))
ax = plt.gca()


plt.plot(target.x, target.y, color='black', marker='o')
for drone in friend_drones:
    plt.plot(drone.x, drone.y, color='blue', marker='o')
    plot_player(ax, drone, pathFinder.DRONE_RADIUS, 'b')

for drone in opponent_drones:
    plt.plot(drone.x, drone.y, color='red', marker='o')
    plot_player(ax, drone, pathFinder.DRONE_RADIUS, 'red')

plot_player(ax, target, 0.02, 'purple')
for p in pathFinder._get_points_around_obstacle(opponent_drones[0]):
    plot_player(ax, p, 0.02, 'brown')

cf_logger.info("path:")
for p,q in zip(path[:-1], path[1:]):
    cf_logger.info('%f %f -> %f %f' % (p.x, p.y, q.x, q.y))
    plt.plot([p.x, q.x], [p.y, q.y], color='green')

plt.xlim(0, max(world_size))
plt.ylim(0, max(world_size))
plt.show()
