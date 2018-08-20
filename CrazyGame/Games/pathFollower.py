import time
import numpy as np
from crazyGame import logger

cf_logger = logger.get_logger(__name__)

POSITION_ALLOWED_RADIUS = 5
MIN_TIME_BETWEEN_DIRECTION_UPDATES = 0.1


class pathFollower:
    def __init__(self, drone, path, orchestrator):
        cf_logger('start new path follower for %s from %s to %s' % (drone.name, path[0], path[-1]))
        self._path = path
        self._orchestrator = orchestrator
        self._drone = drone
        self._generator = self._targets_generator()
        self._target = next(self._generator)
        self._last_direction_modified = time.time()
        self._completed = False
        assert not drone.grounded, 'try to move grounded drone'
        assert self._is_drone_at_position(path[0]), 'drone too far from initial position'

    def follow_path(self):
        if self._completed:
            return
        _time = time.time()
        if _time - self._last_direction_modified < MIN_TIME_BETWEEN_DIRECTION_UPDATES:
            return

        if self._is_drone_at_position(self._target):
            self._target = next(self._generator)
            if self._completed:
                return
        direction = (self._target.x - self._drone.position.x, self._target.y - self._drone.position.y)
        vector = np.array(direction)
        normalized_vector = vector / np.linalg.norm(vector)
        self._orchestrator.try_move_drone(self._drone, normalized_vector.tolist())

    def _is_drone_at_position(self, target):
        return self._drone.position.distance(target) < POSITION_ALLOWED_RADIUS

    def _targets_generator(self):
        for p in self._path[1:]:
            yield p
        self._completed = True
        yield None
