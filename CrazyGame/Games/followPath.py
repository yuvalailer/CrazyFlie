from crazyGame import logger
cf_logger = logger.get_logger(__name__)


class Follower:
    def __init__(self, path, drone, orchestrator):
        cf_logger.info('create new follower')
        self._path = path
        self._drone = drone
        self._orchestrator = orchestrator
        self._completed = False
        self._generator = self._targets_generator()
        self._target = next(self._generator)
        assert not drone.grounded, 'try to move grounded drone'
        current_pos = self._orchestrator.update_drone_xy_pos(self._drone)
        cf_logger.info('pos %s - target %s' %  (current_pos, path[0]))
        assert self._orchestrator.drone_reach_position(self._drone, path[0]), 'drone too far from initial position'

    def follow_path(self):
        if self._completed:
            return True
        if self._orchestrator.drone_reach_position(self._drone, self._target):
            self._target = next(self._generator)
            if self._completed:
                return True
            self._orchestrator.try_goto(self._drone, self._target)
        return False

    @property
    def completed(self):
        return self._completed

    def _targets_generator(self):
        for p in self._path[1:]:
            yield p
        self._completed = True
        yield None
