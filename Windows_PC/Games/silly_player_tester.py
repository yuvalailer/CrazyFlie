import logging
import logger

logger.set_default_debug_level(logging.INFO)
cf_logger = logger.get_logger(__name__)

from shapely.geometry import Point
import matplotlib.pyplot as plt
import silly_player
from datetime import datetime



def plot_player(ax, p, r, c):
    circle =  plt.Circle((p.x, p.y), r, color=c, fill=False)
    ax.add_artist(circle)

friend_drones = [Point(3,4), Point(50,4), Point(50,50)]
opponent_drones = [Point(25,35), Point(22,20), Point(12,20)]
target = Point(25,27)

start_time = datetime.now()
path = silly_player.silly_player_move(friend_drones, opponent_drones, target, 32)
end_time = datetime.now()

elapsed_time = end_time - start_time
cf_logger.info('finding path took %f seconds'%elapsed_time.total_seconds())

plt.figure(figsize=(7,7))
ax = plt.gca()


plt.plot(target.x, target.y, color='black', marker='o')
for drone in friend_drones:
    plt.plot(drone.x, drone.y, color='blue', marker='o')
    plot_player(ax, drone, silly_player.DRONE_RADIUS, 'b')

for drone in opponent_drones:
    plt.plot(drone.x, drone.y, color='red', marker='o')
    plot_player(ax, drone, silly_player.DRONE_RADIUS, 'red')

cf_logger.info("path:")
for p,q in zip(path[:-1], path[1:]):
    cf_logger.info('%d %d -> %d %d' % (p.x, p.y, q.x, q.y))
    plt.plot([p.x, q.x], [p.y, q.y], color='yellow')

plt.xlim(-10, 60)
plt.ylim(-10, 60)
plt.show()