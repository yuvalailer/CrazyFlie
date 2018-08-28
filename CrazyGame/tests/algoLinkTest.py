from CrazyGame.Peripherals import algoLink

algo_link = algoLink.AlgoLink()
algo_link.connect()

algo_link.capture_all_flag_algo([0,0], [2,2,4,4,8,8], [6,6], [12,12])


algo_link.disconnect()

algo_link.connect()