import socket
import time
from shapely.geometry import Point
import logger

cf_logger = logger.get_logger(__name__)

DEFAULT_LOCAL_IP = "127.0.0.1"
DEFAULT_TCP_PORT = 20000
DEFAULT_BUFFER_SIZE = 1024
CONNECTION_TIME_OUT = 2

DRONE_SIZE = 0.5


class AlgoLink:
    def __init__(self, ip=DEFAULT_LOCAL_IP, port=DEFAULT_TCP_PORT, buffer_size=DEFAULT_BUFFER_SIZE):
        self._tcp_ip = ip
        self._tcp_port = port
        self._buffer_size = buffer_size

    def connect(self, number_of_trials=2, time_between_trails=1):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for retry in range(1, number_of_trials + 1):
            try:
                self._socket.settimeout(CONNECTION_TIME_OUT)
                self._socket.connect((self._tcp_ip, self._tcp_port))
                self._socket.settimeout(None)
                return True
            except:
                if retry != number_of_trials:
                    cf_logger.error("Failure {}/{}, No response from {}:{}, Trying again in {} seconds...".format(retry,
                                                                                                                  number_of_trials,
                                                                                                                  self._tcp_ip,
                                                                                                                  self._tcp_port,
                                                                                                                  time_between_trails))
                    time.sleep(time_between_trails)
                else:
                    cf_logger.error(
                        "Failure {}/{}, No response from {}:{}".format(retry, number_of_trials, self._tcp_ip,
                                                                       self._tcp_port))
        raise ConnectionError

    def disconnect(self):
        cf_logger.debug("disconnect")
        self._socket.close()

    def set_world(self, world_size):
        self._send("set_world$%f %f" % (world_size[0] ,world_size[1]))

    def set_drone_size(self, drone_size):
        self._send("set_drone_size$ %f" % drone_size)

    def set_obstacles(self, obstacles):
        pass

    def find_ski_path(self, start_pos, gates):
        cmd = "find_ski_path$%f %f" % (start_pos.x, start_pos.y)
        cmd += "$" + " ".join("%f %f %f %f" % (gate[0].x, gate[0].y, gate[1].x, gate[1].y) for gate in gates)
        res = self._send(cmd)
        if not res:
            raise ConnectionError
        res = res.split(" ")
        print(res)
        ret = []
        for i in range(int(len(res) / 2)):
            ret.append(Point(float(res[2 * i]), float(res[2 * i + 1])))
        return ret

    def capture_all_flags(self, start_pos, sites, friend_drone, opponent_drones):
        cmd = "find_path$%f %f" % (start_pos.x, start_pos.y)
        cmd += "$" + " ".join("%f %f" % (p.x, p.y) for p in sites)
        cmd += "$"
        if friend_drone:
            cmd += "%f %f" % (friend_drone.x, friend_drone.y)
        if opponent_drones:
            cmd += " " + " ".join("%f %f" % (p.x, p.y) for p in opponent_drones)

        res = self._send(cmd)
        if not res:
            raise ConnectionError
        res = res.split(" ")
        print(res)
        ret = []
        for i in range(int(len(res) / 2)):
            ret.append(Point(float(res[2 * i]), float(res[2 * i + 1])))
        return ret

    def _send(self, command):
        try:
            self._socket.send(command.encode())
        except socket.error as e:
            cf_logger.critical("Socket error: {}".format(e))
            return False
        try:
            data = self._socket.recv(self._buffer_size).decode()
            if data and (0 < len(data)):
                cf_logger.debug("Send: '{}' received: '{}'".format(command, data))
                return data
            else:
                cf_logger.critical("The client at the algo link died")
                return False
        except socket.timeout:
            cf_logger.critical("Timeout")
            return False
