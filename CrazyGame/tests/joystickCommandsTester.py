#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logger, time
from dronesController import DronesController
from joystick import Joystick
import time

cf_logger = logger.get_logger(__name__)  # debug(), info(), warning(), error(), exception(), critical()

COMMANDS = ["crazyflie3$Register", "crazyflie3$TakeOff$3$3", "crazyflie3$UP", "crazyflie3$UP", "crazyflie3$LEFT",
            "crazyflie3$LEFT", "crazyflie3$Land", "crazyflie3$UnRegister"]
STARTING_COMMANDS = ["crazyflie3$Register","crazyflie2$Register", "crazyflie3$TakeOff$3$3","crazyflie2$TakeOff$3$3"]
ENDING_COMMANDS = ["crazyflie3$Land","crazyflie2$Land", "crazyflie3$UnRegister", "crazyflie3$UnRegister"]
TURN_TIME = 2
BREAK_TIME = 1


def main():
    dronesController = DronesController()  # Optional variables: "ip", "port" and "buffer_size"
    joystick = Joystick()
    if not dronesController.connect():  # Return True on success and False otherwise
        cf_logger.critical("Communication error")
        exit(0)

    for command in STARTING_COMMANDS: #This always happens anyway
        loop_status = dronesController.send(
            command)  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
        if loop_status == 1:
            cf_logger.error("dronesControllerTester: Failed to execute command: {}".format(command))
        elif loop_status == -1:
            cf_logger.critical("Communication error")
            exit(0)
        time.sleep(1)



    while True:
        timer=time.time()
        while (time.time()-timer)<TURN_TIME:
            goal=joystick.get_normalize_direction()


        time.sleep(BREAK_TIME)










    for command in COMMANDS:
        loop_status = dronesController.send(
            command)  # Return 0 on success, 1 if the VM report on an error and -1 if the connection is closed
        if loop_status == 1:
            cf_logger.error("dronesControllerTester: Failed to execute command: {}".format(command))
        elif loop_status == -1:
            cf_logger.critical("Communication error")
            exit(0)
        time.sleep(1)
    dronesController.disconnect()


if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()
