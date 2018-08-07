from shapely.geometry import LineString
from shapely.geometry import Point
import numpy as np
import math
from queue import PriorityQueue

MARGIN = 1
DRONE_RADIUS = 2
HEXAGON_RADIUS = (DRONE_RADIUS*2 + MARGIN) / np.cos(np.pi/8)
PSIS = [np.pi*psi/4 for psi in range(8)]
HEXAGON_POINTS_VECTORS = [Point(HEXAGON_RADIUS*np.sin(psi), HEXAGON_RADIUS*np.cos(psi)) for psi in PSIS]

MIN_X = 2
MIN_Y = 2
MAX_X = 48
MAX_Y = 48

class SillyPlayer():
    def __init__(self, start_position, target):
        self.target = target
        self.position = start_position

    @property
    def automated(self):
        return True

    @property
    def type(self):
        return 'Silly'

    def path_query(self, opponent, allowed_distance=10):
        path = self._get_full_path(opponent.position)
        path_length = self._path_distance(path)

        if path_length > allowed_distance:
            path = self._get_cut_path(path, allowed_distance)

        return path

    def _path_distance(self, path):
        if len(path) == 0:
            return 0
        return sum(p.distance(q) for p,q in zip([self.position] + path[:-1],path))

    def _in_mincoshky_board(self, p):
        return MIN_X < p.x < MAX_X and MIN_Y < p.y < MAX_Y

    def _get_cut_path(self, path, allowed_distance):
        current_point = self.position
        cut_path = []
        total_distance = 0
        for p in path:
            temp_dis = current_point.distance(p)
            if total_distance + temp_dis  < allowed_distance:
                total_distance += temp_dis
                current_point = p
                cut_path.append(p)
                continue
            else:
                remaining = allowed_distance - total_distance
                remaining_percentage = remaining/temp_dis
                xdiff = p.x - current_point.x
                ydiff = p.y - current_point.y
                cut_path.append(Point(current_point.x + xdiff * remaining_percentage,
                                      current_point.y + ydiff * remaining_percentage))
                break
        return cut_path

    class Node:
        def __init__(self, p):
            self.point = p
            self.distance = math.inf
            self.last = None
            self.visited = False

        def __gt__(self, other):
            return self.distance > other.distance

    def _get_full_path(self, opponent):
        circle = opponent.buffer(DRONE_RADIUS*2 + MARGIN).boundary

        path_to_target = LineString([self.position, self.target])

        assert not self.position.within(circle), 'The drones are too close to each other'

        if self.target.within(opponent.buffer(DRONE_RADIUS*2)):
            path_to_target = LineString([self.position, self.target])
            intersectin_point = circle.intersection(path_to_target)
            assert type(intersectin_point) is Point

            if intersectin_point.distance(self.position) <= MARGIN:
                return [], 0
            return [intersectin_point]

        points = [Point(opponent.x + p.x, opponent.y+p.y) for p in HEXAGON_POINTS_VECTORS]
        points = list(filter(self._in_mincoshky_board, points))

        start_node = self.Node(self.position)
        start_node.distance = 0
        end_node = self.Node(self.target)
        queue = PriorityQueue()
        queue.put(start_node)

        nodes = [self.Node(x) for x in points] + [end_node]

        while not queue.empty():
            current_node = queue.get()
            print('current point %d %d'%(current_node.point.x, current_node.point.y))
            if current_node.visited:
                pass

            if current_node == end_node:
                print("end!!!")
                break

            for temp_node in nodes:
                if temp_node.visited or temp_node == current_node:
                    continue

                print('temp point %d %d' % (temp_node.point.x, temp_node.point.y))

                temp_line = LineString([current_node.point, temp_node.point])
                intersection = circle.intersection(temp_line)
                if len(intersection.geoms) > 0:
                    print("not allowed!")
                    continue

                temp_dis = current_node.distance + current_node.point.distance(temp_node.point)
                if temp_dis < temp_node.distance:
                    print("added!")
                    temp_node.distance = temp_dis
                    temp_node.last = current_node
                    queue.put(temp_node)
        else:
            print("no path found!")
            return []

        print('last for end - %d %d'%(end_node.last.point.x, end_node.last.point.y))
        path = []
        current_node = end_node
        while current_node is not start_node:
            path.append(current_node.point)
            current_node = current_node.last

        path.reverse()
        return path



