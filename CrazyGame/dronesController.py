import logger
import socket
import time

cf_logger = logger.get_logger(__name__)

DEFAULT_TCP_IP = "127.0.0.1"
VM_IP = "172.16.1.2"

DEFAULT_TCP_PORT = 51951
DEFAULT_BUFFER_SIZE = 1024

CONNECTION_TIME_OUT = 1


class DronesController(object):
    def __init__(self, ip=VM_IP, port=DEFAULT_TCP_PORT, buffer_size=DEFAULT_BUFFER_SIZE):
        self._tcp_ip = ip
        self._tcp_port = port
        self._buffer_size = buffer_size

    def connect(self, number_of_trials=2, time_between_trails=1):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(CONNECTION_TIME_OUT)
        for retry in range(number_of_trials):
            try:
                self._socket.connect((self._tcp_ip, self._tcp_port))
            except:
                if retry < number_of_trials - 1:
                    cf_logger.error(
                        "Failure {}/{}, No response from {}:{}, Trying again in {} seconds...".format(
                            retry + 1, number_of_trials, self._tcp_ip, self._tcp_port, time_between_trails))
                    time.sleep(time_between_trails)
                else:
                    cf_logger.error(
                        "Failure {}/{}, No response from {}:{}".format(
                            retry + 1, number_of_trials, self._tcp_ip, self._tcp_port))
        raise ConnectionError

    def send(self, command):  # Return 0 on success, 1 if the Vm report on an error and -1 if the connection is closed
        try:
            self._socket.send(command.encode())
        except socket.error as e:
            cf_logger.critical("Socket error: {}".format(e))
            return -1
        try:
            data = self._socket.recv(self._buffer_size).decode()
            if data == "OK":
                cf_logger.debug("Send: '{}' received: '{}'".format(command, data))
                return 0
            elif data == "FAILED":
                cf_logger.error("Executing '{}' failed".format(command))
            elif data == "FORMAT":
                cf_logger.error("Command '{}' rejected by the VM - Invalid format".format(command))
            elif data == "INVALID":
                cf_logger.error("Command '{}' rejected by the VM - Invalid parameters".format(command))
            elif len(data) == 0:
                cf_logger.critical("The client at the VM died")
                return -1
            else:
                cf_logger.error("Unknown response '{}' from the VM for '{}'".format(data, command))
        except socket.timeout:
            cf_logger.critical("Timeout")
            return -1
        return 1

    def disconnect(self):
        cf_logger.info('disconnect')
        self._socket.close()