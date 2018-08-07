import controlBoardAPI
import joystick
import matplotlib.pyplot as plt

NUMBER_OF_LEDS = 6
try:
    c = controlBoardAPI.ControlBoardAPI()
except:
    c = None
joystick = joystick.Joystick(c)
plt.figure(figsize=(7,7))

ax = plt.gca()
circle =  plt.Circle((0,0), 1, color='black', fill=False)
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
    if lastLn is not None:
        ax.lines.remove(lastLn)
        lastLn = None

    if dir[0] == 0 and dir[1] == 0:
        plt.plot(0, 0, color='pink', marker='o')
    else:
        lastLn, = ax.plot([0, dir[0]], [0, dir[1]], color='b')
    plt.draw()
    plt.pause(0.001)

    if c and c.get_button():
        break
    counter+=1
    if c and counter%100 == 0:
        c.set_led(currentLed,0,0,0)
        currentLed+=1
        if currentLed == NUMBER_OF_LEDS:
            currentLed = 0
        c.set_led(currentLed, 255, 0, 0)

plt.close()
c.disconnect()