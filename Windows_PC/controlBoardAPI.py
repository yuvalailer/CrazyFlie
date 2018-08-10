import serial
import serial.tools.list_ports
import time
import threading
import re
import os

TIME_BETWEEN_MESSAGES = 0.01
LED_MESSAGE_PREFIX = 17
RESET_MESSAGE_BYTE = 89
CALIBRATION_SAMPLES = 10

arduino_message_format = r'^(\d{1,3}) (\d{1,3}) ([01])$'
arduino_message_regex = re.compile(arduino_message_format)


def _get_port():
    if os.name == 'nt':  # if run on windows
        ports = list(serial.tools.list_ports.comports())
        print(ports)
        ports = [str(p) for p in ports if 'USB Serial Port' in str(p)]
        print(ports)
        exit(0)
        assert len(ports) > 0, 'no serial port found'
        if len(ports) == 1:
            return ports[0].split('-')[0].strip()
        return ports[-1].split('-')[0].strip()
    else:  # linux support
        return '/dev/ttyUSB1'


class ControlBoardAPI:
    def __init__(self):
        self._serial_port = _get_port()
        print('serial port name is %s' % self._serial_port)

        self.ser = serial.Serial(self._serial_port, 9600)
        self._data = None
        self._run_thread = True

        self._thread = threading.Thread(target=self._read_joystick)
        self._valuesMutex = threading.Lock()
        self._serMutex = threading.Lock()
        self._thread.start()
        self.reset_leds()
        self._set_defaults()

    def disconnect(self):
        self._run_thread = False
        time.sleep(0.2)

    def set_led(self, led, r, g, b):
        checksum = (LED_MESSAGE_PREFIX + led + r + g + b) % 256
        values = bytearray([LED_MESSAGE_PREFIX, led, r, g, b, checksum])
        self._serMutex.acquire()
        self.ser.write(values)
        self._serMutex.release()

    def reset_leds(self):
        self._serMutex.acquire()
        self.ser.write(bytearray([RESET_MESSAGE_BYTE]))
        self._serMutex.release()

    def get_button(self):
        self._valuesMutex.acquire()
        data = self._data
        self._valuesMutex.release()
        return data.split()[2] == '0'

    def get_joystick_direction(self):
        ax, ay = self._get_joystick_position()
        if abs(ax - self._default_x) < 20 and abs(ay - self._default_y) < 20:
            return [0, 0]

        ax = ax - self._default_x
        ay = ay - self._default_y

        return [ax, ay]

    def _set_defaults(self):
        while True:
            if self._data:
                break
            time.sleep(0.1)
        time.sleep(0.1)
        axs = []
        ays = []
        for _ in range(CALIBRATION_SAMPLES):
            ax, ay = self._get_joystick_position()
            axs.append(ax)
            ays.append(ay)
            time.sleep(0.05)
        self._default_x = max(set(axs), key=axs.count)
        self._default_y = max(set(ays), key=ays.count)
        assert axs.count(self._default_x) > 0.7 * CALIBRATION_SAMPLES, 'default samples are not stable enough - ax'
        assert ays.count(self._default_y) > 0.7 * CALIBRATION_SAMPLES, 'default samples are not stable enough - ay'

    def _get_joystick_position(self):
        self._valuesMutex.acquire()
        data = self._data
        self._valuesMutex.release()
        values = [int(x) for x in data.split()]
        return values[1], values[0]

    def _read_joystick(self):
        while self._run_thread:
            self._serMutex.acquire()
            line = self.ser.readline()
            self._serMutex.release()
            try:
                line = line.decode('UTF-8').rstrip("\r\n")
            except:
                print(line)
                continue

            if arduino_message_regex.match(line):
                self._valuesMutex.acquire()
                self._data = line
                self._valuesMutex.release()
            else:
                print(line)

            time.sleep(TIME_BETWEEN_MESSAGES / 2)
