#!/usr/bin/python
# -*- coding: utf-8 -*-

def setup_path():
	""" Makes sure that all modules are importable """
	import os.path, sys
	
	# relative path to this script
	scriptfile = sys.modules[__name__].__file__
	scriptpath = os.path.dirname(scriptfile) or '.'
	root = os.path.normpath(os.path.join(scriptpath, '..'))
	
	# add rootdir to pythonpath
	sys.path.append(root)

setup_path()

# the actual game server
import server

if __name__ == "__main__":
	server.Server("0.0.0.0", 1234).main()
