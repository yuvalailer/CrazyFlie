import dronesOrchestrator
import logger
from Peripherals import dronesControllerSimulator

cf_logger = logger.get_logger(__name__)
cf_logger.info("#### start drones Orchestrator tester ####")



def main():
    controller = dronesControllerSimulator.DronesController()
    orchestrator = dronesOrchestrator.DronesOrchestrator(controller)
    cf_logger.info("*** world size is - " + str(controller.get_world_size()))
    objects = controller.get_objects()
    cf_logger.info("**********************")
    cf_logger.info("*** The objects in the world are: {}".format(' '.join(objects)))
    cf_logger.info("**********************")

    drones = []
    for object in objects:
        if object[0] == 'c':
            drones.append(object)



if __name__ == "__main__":
    main()