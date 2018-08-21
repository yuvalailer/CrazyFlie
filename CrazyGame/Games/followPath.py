import numpy as np

DESTINATION_RADIUS = 0.05

class Follower:
    def __init__(self, path, drone, orchestrator):
        self._path = path
        self._drone = drone
        self._orchestrator = orchestrator
        self._completed = False
        self._generator = self._targets_generator()
        self._target = next(self._generator)
        assert not drone.grounded, 'try to move grounded drone'
        assert self._is_drone_at_position(path[0]), 'drone too far from initial position'

    def follow_path(self):
        if self._completed:
            return True
        if self._is_drone_at_position(self._target):
            self._target = next(self._generator)
            if self._completed:
                return True
        return self._orchestrator.try_goto(self._drone, self._target)

    def _is_drone_at_position(self, target):
        return np.linalg.norm(self._orchestrator.get_drone_pos(self._drone) - target) < DESTINATION_RADIUS

    def _set_new_path(self, new_path):
        self._path = new_path
        self._completed = False
        self._generator = self._targets_generator()
        self._target = next(self._generator)

    def is_completed(self):
        return self._completed

    def _targets_generator(self):
        for p in self._path[1:]:
            yield p
        self._completed = True
