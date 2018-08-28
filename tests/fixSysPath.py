#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

def test_sys_path():
	try:
		import CrazyGame
	except:
		current_path = os.getcwd()
		if "/CrazyGame" in current_path:
			correct_path = "\nexport PYTHONPATH=\"${PYTHONPATH}:{}\"".format(current_path.rsplit("/CrazyGame", 1)[0])
		else:
			correct_path = ""
		raise ImportError("Failed to load CrazyGame module\nPlease add CrazyGame to PATH environment variable{}".format(correct_path))
