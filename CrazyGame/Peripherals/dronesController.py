import socket
import time
from CrazyGame import logger

cf_logger = logger.get_logger(__name__)

DEFAULT_LOCAL_IP = "127.0.0.1"
DEFAULT_VM_IP = "172.16.1.2"
DEFAULT_TCP_PORT = 51951
DEFAULT_BUFFER_SIZE = 1024
CONNECTION_TIME_OUT = 2

class DronesController:
    def __init__(self, ip=DEFAULT_VM_IP, port=DEFAULT_TCP_PORT, buffer_size=DEFAULT_BUFFER_SIZE):
        self._tcp_ip = ip
        self._tcp_port = port
        self._buffer_size = buffer_size

    def connect(self, number_of_trials=2, time_between_trails=1):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for retry in range(1, number_of_trials+1):
            try:
                self._socket.settimeout(CONNECTION_TIME_OUT)
                self._socket.connect((self._tcp_ip, self._tcp_port))
                self._socket.settimeout(None)
                return True
            except:
                if retry != number_of_trials:
                    cf_logger.error("Failure {}/{}, No response from {}:{}, Trying again in {} seconds...".format(retry, number_of_trials, self._tcp_ip, self._tcp_port, time_between_trails))
                    time.sleep(time_between_trails)
                else:
                    cf_logger.error("Failure {}/{}, No response from {}:{}".format(retry, number_of_trials, self._tcp_ip, self._tcp_port))
        raise ConnectionError

    def disconnect(self):
        cf_logger.debug("disconnect")
        self._socket.close()

    def set_speed(self, speed):
        self._send("SetSpeed${}".format(speed))
    
    def set_step_size(self, step_size):
        self._send("SetStepSize${}".format(step_size))

    def get_world_size(self):
        res = self._send("WorldSize")
        if res and (res.count("$") == 1):
            return [float(x) for x in res.split("$")]
        else:
            cf_logger.error("Failed to get world size")
            return False

    def get_objects(self):
        res = self._send("GetObjects")
        cf_logger.debug("GetObjects got{}".format(res))
        if res and (res != "FATAL"):
            return res.split("$")
        else:
            cf_logger.error("Failed to get list of objects")
            return False

    def take_your_place(self, drone_name, pos): # pos = [x, y]
        self._send("TakeYourPlace${}${}${}".format(drone_name, pos[0], pos[1]))

    def get_object_position(self, object_name):
        res = self._send("GetPos${}".format(object_name))
        if res and (res.count("$") == 2):
            return [float(x) for x in res.split("$")]
        else:
            cf_logger.error("Failed to get position for {}".format(object_name))
            return False

    def move_drone(self, drone_name, direction_vector): # direction_vector = [x, y]
        self._send("MoveDrone${}${}${}".format(drone_name, direction_vector[0], direction_vector[1]))

    def goto(self, drone_name, pos): # pos = [x, y]
        self._send("GoTo${}${}${}".format(drone_name, pos[0], pos[1]))
        cf_logger.debug("{} go to ({},{})".format(drone_name, pos[0], pos[1]))

    def take_off(self, drone_name):
        self._send("TakeOff${}".format(drone_name))
        cf_logger.debug("{} takeoff".format(drone_name))

    def land(self, drone_name):
        self._send("Land${}".format(drone_name))
        cf_logger.debug("{} land".format(drone_name))

    def battery_status(self, drone_name):
        res = self._send("BatteryStatus${}".format(drone_name))
        if res and (res != "FATAL"):
            cf_logger.debug("{} battery is {}".format(drone_name, res))
            return float(res)
        else:
            cf_logger.error("Failed to get battery status for {}".format(drone_name))
            return False

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
                cf_logger.critical("The client at the VM died")
                return False
        except socket.timeout:
            cf_logger.critical("Timeout")
            return False

