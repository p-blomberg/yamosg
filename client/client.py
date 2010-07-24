#!/usr/bin/python
# -*- coding: utf-8 -*-

import shlex, socket, traceback
from select import select

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
				cmd, args = self._parse(self._s.recv(8192))
				self._dispatch(cmd, args)
	
	def _parse(self, line):
		""" Parse a server reply """
		n = len(self._split)
		line = line[:-n]
		tokens = shlex.split(line)
		cmd = tokens.pop(0)
		return cmd, tokens
	
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
