from fixSysPath import test_sys_path
test_sys_path()
import logging
from CrazyGame import logger
logger.set_default_logging_level(logging.INFO)
cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start silly player tester ####")
from shapely.geometry import Point
import matplotlib.pyplot as plt
from Games import pathFinder
from datetime import datetime

def plot_player(ax, p, r, c):
    circle =  plt.Circle((p.x, p.y), r, color=c, fill=False)
    ax.add_artist(circle)

friend_drones = [Point(0.5, 0.5)]
opponent_drones = [Point(1,1), Point(1,0.4)]
target = Point(1.4,1.4)

start_time = datetime.now()
path = pathFinder.find_best_path(friend_drones, opponent_drones, target, 32)
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

cf_logger.info("path:")
for p,q in zip(path[:-1], path[1:]):
    cf_logger.info('%d %d -> %d %d' % (p.x, p.y, q.x, q.y))
    plt.plot([p.x, q.x], [p.y, q.y], color='yellow')

plt.xlim(0, 2)
plt.ylim(0, 2)
plt.show()
