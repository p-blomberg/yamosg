#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path, sys

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

# add rootdir to pythonpath
sys.path.append(root)

import socket, threading, traceback
from select import select
from common.command import parse, Command
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

class Network(threading.Thread):
	def __init__(self, client, host, port):
		threading.Thread.__init__(self)
		self._client = client
		self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._s.connect((host, port))
	
	def run(self):
		while self._client.is_running():
			(rlist, wlist, xlist) = select([self._s], [], [], 1.0)
			if len(rlist) == 0:
				continue
			
			id, cmd, args = parse(self._s.recv(8192))
			
			try:
				self._client.push_command(id, cmd, args)
			except:
				traceback.print_exc()
	
	def send(self, str):
		self._s.send(str)
	
class Client:
	def __init__(self, resolution=(800,600), host='localhost', port=1234, split="\n"):
		self._split = split
		self._running = False
		self._state = StateManager()
		self._state.push(Initial())
		self._network = Network(self, host, port)
		self._command_store = {}
		self._command_queue = []
		self._command_lock = threading.Lock()
		
		self._screen = pygame.display.set_mode(resolution, OPENGL|DOUBLEBUF|RESIZABLE)
		self._resize(resolution[0], resolution[1])
		pygame.display.set_caption('yamosg')
		
		setup_opengl()
	
	def quit(self):
		self._running = False
	
	def is_running(self):
		return self._running
	
	def run(self):
		self._running = True
		self._network.start()
		
		while self._running:
			try:
				self._flush_queue()
				self._logic()
				self._render()
			except:
				traceback.print_exc()
	
	def _resize(self, width, height):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1.0, 1.0);
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
	
	def _flush_queue(self):
		while True:
			self._command_lock.acquire()
			if len(self._command_queue) == 0:
				self._command_lock.release()
				break
		
			command, args = self._command_queue.pop(0)
			self._command_lock.release()
		
			try:
				self._dispatch(command, args)
			except:
				traceback.print_exc()
		
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
			
		except AttributeError:
			print 'Malformed or bad command:', cmd, args
			return
		except:
			print 'Unhandled exception when running command:', cmd, args
			traceback.print_exc()
			return
		
		func(*args)

	def push_command(self, id, command, args):
		# Run from network thread
		
		print id, command, args
		
		try:
			self._command_lock.acquire()
			
			if id == 'UNICAST' or id == 'BROADCAST':
				self._command_queue.append((command, args))
			elif id in self._command_store:
				self._command_store[id].reply(command, args)
			else:
				raise RuntimeError, 'Got a reply for ID ' + id + ' but no matching request'
		finally:
			self._command_lock.release()
	
	def call(self, command, *args):
		cmd = Command(command, *args)
		self._command_lock.acquire()
		self._command_store[cmd.id] = cmd
		print str(cmd)
		self._network.send(str(cmd) + self._split)
		self._command_lock.release()
	
	@expose
	def Hello(self):
		self.call('LOGIN', 'foo', 'bar')

if __name__ == '__main__':
	pygame.display.init()
	
	client = Client()
	client.run()
