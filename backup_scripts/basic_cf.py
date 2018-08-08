#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math, signal, sys, time
import crazyflie, rospy, tf, uav_trajectory
import numpy as np
#import keyboard

CF_NAMES = ["crazyflie3"]

CF_DICT = {}

#################################################
#	(1,0.5,0.5)		(1,-0.9,0.5)	#
#		+-----------------------+	#
#		|			|	#
#	/\	|			|	#
#	|	|			|	#
#	|	|			|	#
#	|	|			|	#
#	|	|			|	#
#	|	|			|	#
#	X	|	 O		|	#
#	|	|			|	#
#	|	|			|	#
#	|	|			|	#
#	|	|			|	#
#	\/	|			|	#
#		|			|	#
#		+-----------------------+	#
#	(-0.7,0.5,0.5)	<--y-->	(-0.7,-0.9,0.5)	#
#################################################

class crazyflie_obj(object):
	_cf = None
	_listener = None
	_name = ""
	_real_pos = (0,0,0)
	def __init__(self, name):
		self._name = name
		self._listener = tf.TransformListener()
		self._cf = crazyflie.Crazyflie(name, name)
		self._cf.setParam("commander/enHighLevel", 1)
		#self.updateLocation()
		print "Starting at ({:.2f},{:.2f},{:.2f})".format(self._real_pos[0],self._real_pos[1],self._real_pos[2])
	def updateLocation(self):
		print "DEBUG updateLocation() for {}".format(self._name) # XXX XXX XXX
		self._real_pos,rot = self._listener.lookupTransform("/world", "/{}".format(self._name), rospy.Time(0))
	def takeoff(self,x=0,y=0,z=0.5):
		z_time = round(abs(self._real_pos[2]-z),2) * 4.0 # How many sec the drone will need in order to be at the requested height
		xy_distance = round(math.sqrt(pow(self._real_pos[0]-x, 2) + pow(self._real_pos[1]-y, 2)),2)
		xy_time = xy_distance * 4.0
		print "Takeoff (This will take {} seconds)".format(z_time)
		self._cf.takeoff(targetHeight=z, duration=z_time)
		time.sleep(z_time)
		print "Going to the start location (This will take {} seconds)".format(xy_time)
		self._cf.goTo(goal=[x,y,z], yaw=0.0, duration=xy_time, relative=False)
		time.sleep(xy_time)
		self.updateLocation()
		print "At ({:.2f},{:.2f},{:.2f}), Should be ({:.2f},{:.2f},{:.2f})".format(self._real_pos[0],self._real_pos[1],self._real_pos[2],x,y,z)
		if self._real_pos[2] < 0.1:
			print "Drone height too low, Aborting..."
			return
	def land(self,landing_duration = 1.5):
		self._cf.land(targetHeight=0.0, duration=landing_duration)
		time.sleep(landing_duration)
		self._cf.stop()

def signal_handler(sig, frame):
	global CF_DICT
	try:
		for cf_name,cf_object in CF_DICT.iteritems():
			cf_object.land()
	finally:
		print "\nCtrl+C pressed"
		sys.exit(0)

def signal_handler_old(sig, frame):
	try:
		stopAllCrazyFlies()
	finally:
		print "\nCtrl+C pressed"
		sys.exit(0)

def stopAllCrazyFlies():
	global CF_LIST
	for cf in [cfs for cfs in CF_LIST if cfs != None]: # Foreach CrazyFlie
		cf.land(targetHeight = 0.0, duration = 1.5)
		time.sleep(1.5)
		cf.stop()

def main():
	signal.signal(signal.SIGINT, signal_handler)
	global CF_NAMES
	global CF_DICT
	for our_cf in CF_NAMES:
		CF_DICT[our_cf] = crazyflie_obj(our_cf)
		CF_DICT[our_cf].takeoff(-0.6, 0.0, 0.5) # Takeoff and get stable at the selected position
		CF_DICT[our_cf].land(landing_duration=2)

def main2_takeoff_and_die():
	signal.signal(signal.SIGINT, signal_handler_old)
	global cf
	rospy.init_node('the_new_gofetch')
	listener = tf.TransformListener()
	cf = crazyflie.Crazyflie(CF_NAMES[0], CF_NAMES[0])
	cf.setParam("commander/enHighLevel", 1)
	(real_x,real_y,real_z), rot = listener.lookupTransform("/world", "/{}".format(CF_NAMES[0]), rospy.Time(0))
	print "Takeoff from ({:.2f} , {:.2f} , {:.2f})".format(real_x,real_y,real_z)
	cf.takeoff(targetHeight = 0.5, duration = 2.0)
	time.sleep(2.0)

def main2():
	signal.signal(signal.SIGINT, signal_handler_old)
	global cf
	rospy.init_node('the_new_gofetch')
	listener = tf.TransformListener()
	cf = crazyflie.Crazyflie(CF_NAMES[0], CF_NAMES[0])
	cf.setParam("commander/enHighLevel", 1)
	(real_x,real_y,real_z), rot = listener.lookupTransform("/world", "/{}".format(CF_NAMES[0]), rospy.Time(0))
	print "Takeoff from ({:.2f} , {:.2f} , {:.2f})".format(real_x,real_y,real_z)
	cf.takeoff(targetHeight = 0.5, duration = 2.0)
	time.sleep(2.0)
	print "Going to start location"
	cf.goTo(goal = [-0.6, 0.0, 0.5], yaw=0.0, duration = 3.0, relative = False)
	time.sleep(3)
	x = -0.6
	while x <= 1.0:
		cf.goTo(goal = [x, 0.0, 0.5], yaw=0.0, duration = 2.0, relative = False)
		time.sleep(2.5)
		(real_x,real_y,real_z), rot = listener.lookupTransform("/world", "/{}".format(CF_NAMES[0]), rospy.Time(0))
		print "At ({:.2f} , {:.2f} , {:.2f}) instead of ({:.2f} , {:.2f} , {:.2f})".format(real_x,real_y,real_z,x,0.0,0.5)
		if real_z < 0.1:
			print "Drone height too low, Aborting..."
			return
		x += 0.2
	time.sleep(5)
	print "Back to (0 , 0 , 0.5)"
	cf.goTo(goal = [0.0, 0.0, 0.5], yaw=0.0, duration = 2.0, relative = False)
	time.sleep(5)
	cf.land(targetHeight = 0.0, duration = 2.0)
	time.sleep(2)
	cf.stop()
	print "Done"

def main3():
	signal.signal(signal.SIGINT, signal_handler_old)
	global cf
	rospy.init_node('the_new_gofetch')
	cf = crazyflie.Crazyflie(CF_NAMES[0], CF_NAMES[0])
	cf.setParam("commander/enHighLevel", 1)
	print "Starting"
	traj1 = uav_trajectory.Trajectory()
	traj1.loadcsv("takeoff.csv")
	traj2 = uav_trajectory.Trajectory()
	traj2.loadcsv("figure8.csv")
	print(traj1.duration)
	cf.uploadTrajectory(0, 0, traj1)
	cf.uploadTrajectory(1, len(traj1.polynomials), traj2)
	cf.startTrajectory(0, timescale=1.0)
	time.sleep(traj1.duration * 2.0)
	cf.startTrajectory(1, timescale=2.0)
	time.sleep(traj2.duration * 2.0)
	cf.startTrajectory(0, timescale=1.0, reverse=True)
	time.sleep(traj1.duration * 1.0)
	cf.stop()
	print "Done"

if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print e