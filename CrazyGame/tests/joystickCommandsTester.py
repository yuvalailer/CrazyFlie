import logger
import sys
import pygame
import time
from fixSysPath import test_sys_path
test_sys_path()
from CrazyGame.dronesController import DronesController
from CrazyGame.joystick import Joystick

cf_logger = logger.get_logger(__name__)  # debug(), info(), warning(), error(), exception(), critical()

DRONES = []
TIME = 0.1


def main():
    for drone_name in sys.argv:  # insert all drones
            DRONES.append(drone_name)
    del DRONES[0]
    current = 0  # the drone that's controlled now
    drones_cont = DronesController()  # Optional variables: "ip", "port" and "buffer_size"
    joystick = Joystick(None)
    if not drones_cont.connect():  # Return True on success and False otherwise
        cf_logger.critical("Communication error")
        exit(0)

    while True:
        timer = time.time()
        cmd = joystick.get_normalize_direction()
        drones_cont.move_drone(DRONES[current], cmd)
        while time.time()-timer < TIME:
            time.sleep(0.001)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            current = (current+1) % (len(DRONES))
        elif keys[pygame.K_ESCAPE]:
            break
    drones_cont.disconnect()


if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()
