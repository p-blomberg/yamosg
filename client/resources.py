#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import sys

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

real_open = open

def open(name, mode='r'):
	global root

	if not isinstance(name, basestring):
		name = os.path.join(*name)

	return real_open(os.path.join(root, name), mode)
