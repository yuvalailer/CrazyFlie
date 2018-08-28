from Peripherals import algoLink
from shapely.geometry import Point
import logger

link = algoLink.AlgoLink()

link.connect()

start_pos = Point(0,0)
gates = [[Point(2,3), Point(3, 2)], [Point(17, 29), Point(18, 28)], [Point(27, 3), Point(26, 4)]]

link.find_ski_path(start_pos, gates)


link.disconnect()

