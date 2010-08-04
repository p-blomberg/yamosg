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
import json
from select import select
from common.command import parse, parse_tokens, Command
from common.vector import Vector2i, Vector3
from state import Initial, StateManager
from entity import Entity
from state.game import Game as GameState
from game import GameWidget
from ui.container import Container
from ui.window import Window

import pygame
from pygame.locals import *
from OpenGL.GL import *


def expose(func):
	""" Exposes a method, eg is callable by server """
	func.exposed = True
	return func

def server_call(alias):
	def wrap(f):
		def wrapped_f(self, *args, **kwargs):
			status, args2, line = self.call(alias, *args, **kwargs)
			f(self, status, line, *args2)
		return wrapped_f
	return wrap

def setup_opengl():
	glClearColor(1,0,1,0)
	glEnable(GL_TEXTURE_2D)
	
	glEnable(GL_BLEND);
	#glDisable(GL_ALPHA_TEST);
	#glDisable(GL_DEPTH_TEST);
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

def have_trailing_newline(line):
	return line[-1] == '\n' or line[-1] == '\r' or line[-2:] == '\r\n'

class Network(threading.Thread):
	def __init__(self, client, host, port):
		threading.Thread.__init__(self)
		self._client = client
		self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._s.connect((host, port))
	
	def run(self):
		tail = ''
		while self._client.is_running():
			(rlist, wlist, xlist) = select([self._s], [], [], 1.0)
			if len(rlist) == 0:
				continue
			
			data = tail + self._s.recv(8192)
			tail = ''
			
			lines = data.splitlines()
				
			# store tail
			if not have_trailing_newline(data):
				tail = lines.pop()
			
			for line in lines:
				self._client.push_command(line)
	
	def send(self, str):
		self._s.send(str)

class Client:
	def __init__(self, resolution=Vector2i(800,600), host='localhost', port=1234, split="\n"):
		# opengl must be initialized first
		self._screen = pygame.display.set_mode(resolution.xy(), OPENGL|DOUBLEBUF|RESIZABLE)
		pygame.display.set_caption('yamosg')
		setup_opengl()
		
		self._resolution = resolution
		self._split = split
		self._running = False
		self._state = StateManager()
		self._game = GameWidget(resolution)
		self._state.push(GameState(resolution, Container(Vector2i(0,0), resolution, children=[self._game, Window(Vector2i(100,100), Vector2i(320,240))])))
		self._network = Network(self, host, port)
		self._command_store = {}
		self._command_queue = []
		self._command_lock = threading.Lock()
		self._playerid = None

		# resizing must be done after state has been created so the event is propagated proper.
		self._resize(resolution)
	
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
			except GLError:
				traceback.print_exc()
				self.quit()
			except:
				traceback.print_exc()
	
	def _resize(self, resolution):
		self._resolution = resolution
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, resolution.width, 0, resolution.height, -1.0, 1.0);
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self._state.resize(resolution)
	
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
				pos = Vector2i(event.pos)
				pos.y = self._resolution.height - pos.y
				self._state.on_mousemove(pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				pos = Vector2i(event.pos)
				pos.y = self._resolution.height - pos.y
				self._state.on_buttondown(pos, event.button)
			elif event.type == pygame.MOUSEBUTTONUP:
				pos = Vector2i(event.pos)
				pos.y = self._resolution.height - pos.y
				self._state.on_buttonup(pos, event.button)
			elif event.type == pygame.KEYDOWN:
				pass
			elif event.type == pygame.KEYUP:
				pass
			else:
				print 'Unhandled pygame event', event
	
	def _render(self):
		glClearColor(1,0,0,0)
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

	def push_command(self, line):
		# Run from network thread
		
		try:
			self._command_lock.acquire()
			
			tokens = parse_tokens(line)
			id = tokens[0]
			if id == 'UNICAST' or id == 'BROADCAST':
				id, command, args = parse(line)
				self._command_queue.append((command, args))
			elif id in self._command_store:
				status = tokens[1]
				args = tuple(tokens[2:])
				data = line[len(id)+len(status)+2:]

				self._command_store[id].reply(status, args, data)
			else:
				raise RuntimeError, 'Got a reply for ID ' + id + ' but no matching request'
		except:
			traceback.print_exc()
		finally:
			self._command_lock.release()
	
	def call(self, command, *args):
		"""
			Synchronously call and get reply
		"""
		cmd = Command(command, *args)
		
		# send command
		with self._command_lock:
			self._command_store[cmd.id] = cmd
			self._network.send(str(cmd) + self._split)
		
		# await reply
		reply = cmd.wait()
		
		# delete command
		with self._command_lock:
			del self._command_store[cmd.id]
		
		return reply
	
	@server_call('LIST_OF_ENTITIES')
	def list_of_entities(self, status, line, *args):
		if status == 'NOT_OK':
			return
		
		self._game.entities = [Entity(**x) for x in json.loads(line)]
	
	@expose
	def Hello(self):
		self.call('SET', 'ENCODER', 'json')
		_, self.playerid, _ = self.call('LOGIN', 'foo', 'bar')
		self.list_of_entities()
		#_, entities = self.call('LIST_OF_ENTITIES')
		#print json.loads(entities)

if __name__ == '__main__':
	pygame.display.init()
	
	client = Client()
	client.run()
