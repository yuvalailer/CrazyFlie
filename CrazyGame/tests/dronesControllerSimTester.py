from CrazyGame import dronesControllerSimulator
import logger
import time

cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start controller sim tester ####")

def main():
    controller = dronesControllerSimulator.DronesController()
    print("world size is - {}"%controller.get_world_size())

    objects = controller.get_objects()
    print("The objects in the world are: {}"%' '.join(objects))

    drones = []
    for object in objects:
        if object[0] == 'c':
            drones.append(object)

    for drone in drones:
        controller.take_off(drone)

    for drone in drones:
        print(controller.get_object_position(drone))

    drone = drones[0]
    controller.move_drone(drone, (0.6, 0.8))
    now = time.time()
    while now < 1.5 :
        print(controller.get_object_position(drone))
        print(now)
        time.sleep(0.1)






if __name__ == "__main__":
    main()