import functools
import math
from queue import PriorityQueue

import numpy as np
from shapely.geometry import LineString
from shapely.geometry import Point

import dronesOrchestrator
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

MARGIN = 0.1
DRONE_RADIUS = dronesOrchestrator.DRONE_RADIUS * 1
HEXAGON_RADIUS = (DRONE_RADIUS * 2 + MARGIN) / np.cos(np.pi/8)
PSIS = [np.pi*psi/4 for psi in range(8)]
HEXAGON_POINTS_VECTORS = [Point(HEXAGON_RADIUS*np.sin(psi), HEXAGON_RADIUS*np.cos(psi)) for psi in PSIS]


def _path_distance(path):
    return sum(p.distance(q) for p, q in zip(path[:-1], path[1:]))


def _in_minkowski_board(p, min_x, max_x, min_y, max_y):
    return min_x <= p.x <= max_x and min_y <= p.y <= max_y


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


def _handle_edge(current_node, temp_node, queue, segment_query):
    cf_logger.debug('\t temp node %s ' % temp_node.point)
    if temp_node.visited or temp_node == current_node:
        cf_logger.debug('\t\tvisited')
        return

    temp_line = LineString([current_node.point, temp_node.point])
    if not segment_query(temp_line):
        cf_logger.debug('\t\tnot allowed')
        return

    temp_dis = current_node.distance + current_node.point.distance(temp_node.point)
    if temp_dis < temp_node.distance:
        cf_logger.debug('\t\tadd edge')
        temp_node.distance = temp_dis
        temp_node.last = current_node
        queue.put(temp_node)


def _extract_path(end_node, start_node):
    path = []
    current_node = end_node
    while current_node is not start_node:
        path.append(current_node.point)
        current_node = current_node.last

    path.append(start_node.point)
    path.reverse()
    return path


def _set_diajstra_base_conditions(start, target, points):
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

    return queue, start_node, end_node, [Node(x) for x in points] + [end_node]


def _diajstra_path_finder(start, target, points, segment_query):
    queue, start_node, end_node, nodes = _set_diajstra_base_conditions(start, target, points)

    while not queue.empty():
        current_node = queue.get()
        cf_logger.debug(current_node.point)
        if current_node.visited:
            pass

        if current_node == end_node:
            break

        for temp_node in nodes:
            _handle_edge(current_node, temp_node, queue, segment_query)

    else:
        cf_logger.warning("no path found!")
        return None

    return _extract_path(end_node, start_node)


def _get_points_around_obstacle(obstacle):
    return [Point(obstacle.x + p.x, obstacle.y + p.y) for p in HEXAGON_POINTS_VECTORS]


def _points_to_circle_obstacles(points, radius=DRONE_RADIUS*2):
    return [p.buffer(radius) for p in points]


def _is_point_legal(circle_obstacles, min_x, max_x, min_y, max_y, p):
    if not _in_minkowski_board(p, min_x, max_x, min_y, max_y):
        return False

    for obs in circle_obstacles:
        if p.within(obs):
            return False

    return True


def _segment_intersection_query(circle_obstacles, line):  # assumes line points are legal
    for circle in circle_obstacles:
        inter = circle.intersection(line)
        if inter.type == 'LineString':
            return False

    return True


def _find_path(start, target, obstacles, min_x, max_x, min_y, max_y):
    cf_logger.info('find path from %s to %s'%(start, target))
    circle_obstacles = _points_to_circle_obstacles(obstacles)
    point_query = functools.partial(_is_point_legal, circle_obstacles, min_x, max_x, min_y, max_y)
    points = []
    for obstacle in obstacles:
        points.extend(list(filter(point_query, _get_points_around_obstacle(obstacle))))

    if not point_query(target):
        cf_logger.info('target not reachable!')
        new_target = sorted(points, key=lambda k: target.distance(k))[0]
        target_moved_distance, target = target.distance(new_target), new_target
    else:
        target_moved_distance=0

    segment_query = functools.partial(_segment_intersection_query, circle_obstacles)
    cf_logger.debug('run diajstra:')
    path = _diajstra_path_finder(start, target, points, segment_query)

    return path, target_moved_distance


def find_best_path(friend_drones, opponent_drones, target, min_x, max_x, min_y, max_y):
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
        path, target_moved_distance = _find_path(drone, target, temp_drones, min_x, max_x, min_y, max_y)
        if path:
            paths.append(Path(path, target_moved_distance))
            cf_logger.debug('found path from %s. path distance - %d. target_moved - %d'%
                            (drone, paths[-1].distance, target_moved_distance))

    paths = sorted(paths)
    if len(paths) == 0:
        cf_logger.info('failed to find a path! print board for debugging')
        cf_logger.info('friend_drones:')
        for drone in friend_drones:
            cf_logger.info('\t%s' % drone)
        cf_logger.info('opponent_drones:')
        for drone in opponent_drones:
            cf_logger.info('\t%s' % drone)
        cf_logger.info('target:')
        cf_logger.info(target)
        cf_logger.info('DRONE_RADIUS - %f' % DRONE_RADIUS)
        return None
    return paths[0].path
