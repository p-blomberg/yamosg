#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path, sys

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

# add rootdir to pythonpath
sys.path.append(root)

import socket, traceback
from select import select
from common import command

def expose(func):
	""" Exposes a method, eg is callable by server """
	func.exposed = True
	return func

class Client:
	def __init__(self, host='localhost', port=1234, split="\n"):
		self._split = split
		self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._s.connect((host, port))
		self._running = False
		
	def run(self):
		self._running = True
		while self._running:
			(rlist, wlist, xlist) = select([self._s], [], [], 0.0)
			
			if len(rlist) > 0:
				cmd, args = command.parse(self._s.recv(8192))
				self._dispatch(cmd, args)
	
	def _dispatch(self, cmd, args):
		""" Run command """
		
		try:
			# Try to get function
			func = getattr(self, cmd)
			
			# See if it is exposed, so a malicious cannot run any func.
			if not getattr(func, 'exposed'):
				raise AttributeError # raised to get same handling as a non-existing func.
			
			func(*args)
			
		except AttributeError:
			print 'Malformed or bad command:', cmd, args
		except:
			print 'Unhandled exception when running command:', cmd, args
			traceback.print_exc()

	@expose
	def Hello(self):
		print 'got hello'

if __name__ == '__main__':
	client = Client()
	client.run()
