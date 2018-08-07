import serial
import time
import threading
import re

TIME_BETWEEN_MESSAGE = 0.01
LED_MESSAGE_PREFIX = 17
RESET_MESSAGE_BYTE = 89

pattern = '^(\d{1,3}) (\d{1,3}) (0|1)'
regex = re.compile(r'^(\d{1,3}) (\d{1,3}) ([01])$')


class ControlBoardAPI():
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB1', 9600)
        self._ax = -1
        self._ay = -1
        self._button = False
        self._run_thread = True

        self._thread = threading.Thread(target=self._read_joystick)
        self._valuesMutex = threading.Lock()
        self._serMutex = threading.Lock()
        self._thread.start()
        self.reset_leds()
        self._set_defaults()


    def disconnect(self):
        self._run_thread = False
        time.sleep(0.5)

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
        _button = self._button
        self._valuesMutex.release()
        return _button

    def get_joystick_direction(self):
        ax, ay = self._get_joystick_position()
        if abs(ax-self._default_x) < 20 and abs(ay-self._default_y) < 20:
            return [0, 0]

        ax = ax - self._default_x
        ay = ay - self._default_y

        return [ax, ay]

    def _set_defaults(self):
        NUMBER_OF_SAMPLES = 10
        while True:
            ax, ay = self._get_joystick_position()
            if ax != -1 and ay != -1:
                break
            time.sleep(0.1)
        time.sleep(0.2)
        axs = []
        ays = []
        for _ in range(NUMBER_OF_SAMPLES):
            ax, ay = self._get_joystick_position()
            axs.append(ax)
            ays.append(ay)
            time.sleep(0.1)
        self._default_x = max(set(axs), key=axs.count)
        self._default_y = max(set(ays), key=ays.count)
        assert axs.count(self._default_x) > 0.7 * NUMBER_OF_SAMPLES
        assert ays.count(self._default_y) > 0.7 * NUMBER_OF_SAMPLES



    def _get_joystick_position(self):
        self._valuesMutex.acquire()
        temp_ax, temp_ay = self._ax, self._ay
        self._valuesMutex.release()
        return temp_ax, temp_ay

    def _read_joystick(self):
        while self._run_thread:
            self._serMutex.acquire()
            line = self.ser.readline()
            self._serMutex.release()
            try:
                line = line.decode('UTF-8').rstrip("\r\n")
            except:
                print(line)
            if not regex.match(line):
                print(line)
                time.sleep(TIME_BETWEEN_MESSAGE/2)
                continue
            values = [int(x) for x in line.split()]
            self._valuesMutex.acquire()
            self._ax, self._ay, self._button = values[0], values[1], int(values[2]) == 0
            self._valuesMutex.release()

            time.sleep(TIME_BETWEEN_MESSAGE/2)