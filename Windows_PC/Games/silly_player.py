from shapely.geometry import LineString
from shapely.geometry import Point
from queue import PriorityQueue
import functools
import numpy as np
import math
import logger

cf_logger = logger.get_logger(__name__)

MIN_X = 2
MIN_Y = 2
MAX_X = 48
MAX_Y = 48

MARGIN = 1
DRONE_RADIUS = 2
HEXAGON_RADIUS = (DRONE_RADIUS*2 + MARGIN) / np.cos(np.pi/8)
PSIS = [np.pi*psi/4 for psi in range(8)]
HEXAGON_POINTS_VECTORS = [Point(HEXAGON_RADIUS*np.sin(psi), HEXAGON_RADIUS*np.cos(psi)) for psi in PSIS]


def _path_distance(path):
    return sum(p.distance(q) for p,q in zip(path[:-1],path[1:]))


def _in_minkowski_board(p):
    return MIN_X < p.x < MAX_X and MIN_Y < p.y < MAX_Y


def _cut_path(path, allowed_distance):
    new_path = [path[0]]
    total_distance = 0
    for p,q in zip(path[:-1],path[1:]):
        temp_dis = p.distance(q)
        if total_distance + temp_dis < allowed_distance:
            total_distance += temp_dis
            new_path.append(q)
            continue
        else:
            remaining = allowed_distance - total_distance
            remaining_percentage = remaining / temp_dis
            x_diff = q.x - p.x
            y_diff = q.y - p.y
            new_path.append(Point(p.x + x_diff * remaining_percentage,
                                  p.y + y_diff * remaining_percentage))
            break
    return new_path


def _diajstra_path_finder(start, target, points, segment_query):
    class Node:
        def __init__(self, p, distance=math.inf):
            self.point = p
            self.distance = distance
            self.last = None
            self.visited = False

        def __gt__(self, other):
            return self.distance > other.distance

    start_node = Node(start, 0)
    end_node = Node(target)
    queue = PriorityQueue()
    queue.put(start_node)

    nodes = [Node(x) for x in points] + [end_node]

    while not queue.empty():
        current_node = queue.get()
        cf_logger.debug(current_node.point)
        if current_node.visited:
            pass

        if current_node == end_node:
            break

        for temp_node in nodes:
            cf_logger.debug('\t temp node %s '%temp_node.point)
            if temp_node.visited or temp_node == current_node:
                cf_logger.debug('\t\tvisited')
                continue

            temp_line = LineString([current_node.point, temp_node.point])
            if not segment_query(temp_line):
                cf_logger.debug('\t\tnot allowed')
                continue

            temp_dis = current_node.distance + current_node.point.distance(temp_node.point)
            if temp_dis < temp_node.distance:
                cf_logger.debug('\t\tadd edge')
                temp_node.distance = temp_dis
                temp_node.last = current_node
                queue.put(temp_node)
    else:
        cf_logger.warning("no path found!")
        return None

    path = []
    current_node = end_node
    while current_node is not start_node:
        path.append(current_node.point)
        current_node = current_node.last

    path.append(start)
    path.reverse()
    return path


def _get_points_around_obstacle(obstacle):
    return [Point(obstacle.x + p.x, obstacle.y + p.y) for p in HEXAGON_POINTS_VECTORS]


def _points_to_circle_obstacles(points, radius=DRONE_RADIUS*2):
    return [p.buffer(radius) for p in points]


def _is_point_legal(circle_obstacles, p):
    if not _in_minkowski_board(p):
        return False

    for obs in circle_obstacles:
        if p.within(obs):
            return False

    return True


def _segment_intersection_query(circle_obstacles, line): #assumes line points are legal
    for circle in circle_obstacles:
        inter = circle.intersection(line)
        if inter.type == 'LineString':
            return False

    return True


def _find_path(start, target, obstacles):
    cf_logger.info('find path from %s to %s'%(start, target))
    circle_obstacles = _points_to_circle_obstacles(obstacles)
    point_query = functools.partial(_is_point_legal, circle_obstacles)
    points = []
    for obstacle in obstacles:
        cf_logger.debug('get obstackes %s points:'%obstacle)
        obstacle_points = _get_points_around_obstacle(obstacle)
        obstacle_points = list(filter(point_query, obstacle_points))
        for p in obstacle_points:
            points.append(p)

    if not point_query(target):
        cf_logger.info('obstacle not reacable!')
        new_target = sorted(points, key=lambda k: target.distance(k))[0]
        target_moved_distance = target.distance(new_target)
        target = new_target
    else:
        target_moved_distance=0

    segment_query = functools.partial(_segment_intersection_query, circle_obstacles)
    cf_logger.debug('run diajstra:')
    path = _diajstra_path_finder(start, target, points, segment_query)
    if not path:
        return None, 0

    return path, target_moved_distance


def silly_player_move(friend_drones, opponent_drones, target, allowed_distance=20):
    @functools.total_ordering
    class Path:
        def __init__(self, path, target_moved_distance):
            self.path = path
            self.target_moved_distance = target_moved_distance
            self.distance = _path_distance(self.path)

        def __lt__(self, other):
            if self.target_moved_distance != other.target_moved_distance:
                return self.target_moved_distance < other.target_moved_distance

            return self.distance < other.distance

    paths = []
    drones = friend_drones + opponent_drones
    for drone in friend_drones:
        temp_drones = list(drones)
        temp_drones.remove(drone)
        path, target_moved_distance = _find_path(drone, target, temp_drones)
        if path:
            paths.append(Path(path, target_moved_distance))
            cf_logger.debug('found path from %s. path distance - %d. target_moved - %d'%
                            (drone, paths[-1].distance, target_moved_distance))

    paths = sorted(paths)
    return _cut_path(paths[0].path, allowed_distance)
