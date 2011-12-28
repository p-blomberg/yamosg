#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import sys

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

real_open = open

def realpath(name):
	global root
	if not isinstance(name, basestring):
		name = os.path.join(*name)
	return os.path.join(root, name)

def open(name, mode='r'):
	return real_open(realpath(name), mode)
