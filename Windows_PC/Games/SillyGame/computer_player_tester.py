from shapely.geometry import Point
import matplotlib.pyplot as plt
import computer_player

def plot_player(ax, p, r, c):
    circle =  plt.Circle((p.position.x, p.position.y), r, color=c, fill=False)
    ax.add_artist(circle)

player = computer_player.SillyPlayer(Point(3,4), Point(25,25))
opponent = computer_player.SillyPlayer(Point(20,20), Point(40,5))

points = [Point(opponent.position.x + p.x, opponent.position.y+p.y) for p in computer_player.HEXAGON_POINTS_VECTORS]

path = player.path_query(opponent, 33)

plt.figure(figsize=(7,7))

plt.plot(player.target.x, player.target.y, color='black', marker='o')
for p in points:
    plt.plot(p.x, p.y, color='pink', marker='o')

path = [Point(3,4)] + path
print("path:")
for p,q in zip(path[:-1], path[1:]):
    print('%d %d -> %d %d' % (p.x, p.y, q.x, q.y))
    plt.plot([p.x, q.x], [p.y, q.y], color='b')

ax = plt.gca()
plot_player(ax, player, computer_player.DRONE_RADIUS, 'g')
plot_player(ax, opponent, computer_player.DRONE_RADIUS, 'r')

plt.xlim(-10, 60)
plt.ylim(-10, 60)
plt.show()