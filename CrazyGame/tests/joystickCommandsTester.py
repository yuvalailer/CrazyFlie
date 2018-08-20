import logger, sys, pygame, time
from fixSysPath import test_sys_path
test_sys_path()
from CrazyGame.dronesController import DronesController
from CrazyGame.joystick import Joystick

cf_logger = logger.get_logger(__name__) # debug(), info(), warning(), error(), exception(), critical()

DRONES = []
TIME = 0.1

def main():
	drones_cont = DronesController() # Optional variables: "ip", "port" and "buffer_size"
	if not drones_cont.connect(number_of_trials=5, time_between_trails=3):
		cf_logger.critical("Communication error")
		return
	for drone_name in drones_cont.get_objects():
		DRONES.append(drone_name)
		drones_cont.take_off(drone_name)
	current = 0 # the drone that's controlled now
	joystick = Joystick(None)
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
	for drone_name in DRONES:
		drones_cont.land(drone_name)
	drones_cont.disconnect()

if __name__ == "__main__":
    cf_logger.info("######################################################")
    cf_logger.info("####                   Started                    ####")
    cf_logger.info("######################################################")
    main()
