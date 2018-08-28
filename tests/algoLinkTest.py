from Peripherals import algoLink
from shapely.geometry import Point

algo_link = algoLink.AlgoLink()
algo_link.connect()

#algo_link.capture_all_flags([0,0], [2,2,4,4,8,8], [6,6], [12,12])

algo_link.capture_all_flags(Point(0,0), [Point(2,2), Point(4,4), Point(8,8)], Point(6,6), [Point(12,12)])


algo_link.disconnect()

algo_link.connect()