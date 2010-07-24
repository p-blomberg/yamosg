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
from common.vector import Vector
from state import Initial, StateManager

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def expose(func):
	""" Exposes a method, eg is callable by server """
	func.exposed = True
	return func

def setup_opengl():
	glClearColor(1,0,1,0)
	
class Client:
	def __init__(self, resolution=(800,600), host='localhost', port=1234, split="\n"):
		self._split = split
		self._running = False
		self._state = StateManager()
		self._state.push(Initial())
		
		self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._s.connect((host, port))
		
		self._screen = pygame.display.set_mode(resolution, OPENGL|DOUBLEBUF|RESIZABLE)
		self._resize(resolution[0], resolution[1])
		pygame.display.set_caption('yamosg')
		
		setup_opengl()
	
	def quit(self):
		self._running = False
	
	def run(self):
		self._running = True
		while self._running:
			self._network()
			self._logic()
			self._render()
	
	def _resize(self, width, height):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1.0, 1.0);
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
	
	def _network(self):
		(rlist, wlist, xlist) = select([self._s], [], [], 0.0)
			
		if len(rlist) > 0:
			id, cmd, args = command.parse(self._s.recv(8192))
			self._dispatch(cmd, args)
	
	def _logic(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.quit()
			elif event.type == pygame.VIDEOEXPOSE:
				pass
			elif event.type == pygame.VIDEORESIZE:
				self._resize(event.w, event.h)
			elif event.type == pygame.ACTIVEEVENT:
				pass
			elif event.type == pygame.MOUSEMOTION:
				pass
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self._state.on_buttondown(Vector(event.pos), event.button)
				pass
			elif event.type == pygame.MOUSEBUTTONUP:
				pass
			elif event.type == pygame.KEYDOWN:
				pass
			elif event.type == pygame.KEYUP:
				pass
			else:
				print 'Unhandled pygame event', event
	
	def _render(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self._state.render()
		pygame.display.flip()
	
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
	pygame.display.init()
	
	client = Client()
	client.run()
