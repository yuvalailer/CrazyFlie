import logger

cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start silly player tester ####")

import controlBoardAPI
import joystick
import matplotlib.pyplot as plt

NUMBER_OF_LEDS = 6
try:
    control_board_api = controlBoardAPI.ControlBoardAPI()
except Exception as e:
    cf_logger.warning('connection to Board failed by Exception - %s' % e)
    control_board_api = None
joystick = joystick.Joystick(control_board_api)
plt.figure(figsize=(7, 7))

ax = plt.gca()
circle = plt.Circle((0, 0), 1, color='black', fill=False)
ax.add_artist(circle)
plt.xlim(-2, 2)
plt.ylim(-2, 2)
plt.ion()
plt.show()

currentLed = 0
counter = 0

lastLn = None
while True:
    dir = joystick.get_normalize_direction()
    if lastLn:
        ax.lines.remove(lastLn)
        lastLn = None

    if dir[0] == 0 and dir[1] == 0:
        plt.plot(0, 0, color='pink', marker='o')
    else:
        lastLn, = ax.plot([0, dir[0]], [0, dir[1]], color='b')
    plt.draw()
    plt.pause(0.001)

    if joystick.get_click():
        break

    counter += 1
    if control_board_api and counter % 100 == 0:
        control_board_api.set_led(currentLed, 0, 0, 0)
        currentLed += 1
        if currentLed == NUMBER_OF_LEDS:
            currentLed = 0
            control_board_api.set_led(currentLed, 255, 0, 0)

plt.close()
control_board_api.disconnect()
