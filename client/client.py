#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path, sys, platform as pf

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

# add rootdir to pythonpath
sys.path.append(root)
if pf.system() == 'Darwin':
	sys.path.append(os.path.join(root, 'deps', 'osx_lion', 'site-packages'))
	sys.path.append(os.path.join(root, 'deps', 'osx_lion', 'site-packages', 'gtk-2.0'))

import socket, threading, traceback
import json
from signal import signal, SIGINT
from select import select
from common.command import parse, parse_tokens, Command
from common.vector import Vector2i, Vector3
from state import Initial, StateManager
from entity import Entity
from state.game import Game as GameState
from game import GameWidget
from ui.composite import Composite
from ui.box import HBox, VBox
from ui.window import SampleCairoWindow, SampleOpenGLWindow
from ui.toolbar import Toolbar
from ui.layout import LayoutAttachment
import pygame
from pygame.locals import *
from OpenGL.GL import *
import itertools
from common.logger import Log
import logging.config

event_table = {}
def event(type, adapter=lambda x:x):
    def wrapper(func):
        event_table[type] = func, adapter
        return func
    return wrapper

def expose(func):
	""" Exposes a method, eg is callable by server """
	func.exposed = True
	return func

network_log = None

def server_call(alias, *in_args, **params):
	"""
	Wrapper for a server call.

	:param alias: is the name of the server call.
	:param in_args: is the names of the arguments (as strings.)
	:param raw: if True the raw reply will be passed instead of parsed into positional arguments.
	:param decode: if True the reply will be json decoded.

	eg:

	@server_call('FOO', 'spam', 'bacon')
	def foo(self, fred, barney, wilma):
		pass

	will make a function `foo(self, spam, bacon)`
	which calls the user implemented function with the reply
	from the server and arguments passed as *args

	Calling foo(1, 2) yields the server command 'FOO 1 2' and
	if the reply is 'OK a b c' user function will be called as
	foo('a', 'b', 'c')

	It accepts both positional- and keyword arguments.
	"""

	raw = params.get('raw', False)
	decode = params.get('decode', False)
	en = len(in_args) # expected number of arguments

	def wrap(f):
		def wrapped_f(self, *args, **kwargs):
			global network_log
			
			# parse varargs. Parsed before arg count checking because
			# varargs aren't counted in the expected number.
			varargs = []
			if 'varargs' in kwargs:
				varargs = kwargs['varargs']
				del kwargs['varargs']

			# make sure the correct number of arguments is passed
			gn = len(args) + len(kwargs) # passed number of arguments
			if gn != en:
				raise TypeError, '%s takes exactly %d argument%s (%d given)' % (alias, en, en > 1 and 's' or '', gn)
			
			# parse arguments into a new args list
			d = dict(itertools.izip_longest(in_args, args, fillvalue=None))
			d.update(kwargs)
			real_args = [d.pop(k) for k in in_args]
			real_args += varargs

			# pass command to server
			network_log.debug('calling %s(%s)', alias, ', '.join([str(x) for x in real_args]))
			status, reply_args, line = self.call(alias, *real_args)
			network_log.debug('reply: %s', line)
			if status != 'OK':
				raise RuntimeError, reply_args[0]

			# pass reply to callback
			try:
				if decode:
					decoded = None
					if line != '': # handle when servery reply is empty
						decoded = json.loads(line)
					return f(self, decoded)
				elif raw:
					return f(self, line)
				else:
					return f(self, *reply_args)
			except:
				traceback.print_exc()
				print 'server reply was:', line
				return None

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
	cursor_default = None
	cursor_capture = None

	def __init__(self, resolution=Vector2i(800,600), host='localhost', port=1234, split="\n"):
		global network_log
		
		self.log = Log('client')
		network_log = Log('network')

		# must have at least one handler
		self.log.logger.addHandler(logging.NullHandler())
		network_log.logger.addHandler(logging.NullHandler())
		
		# opengl must be initialized first
		self.log.info("Initializing display (windowed at %(resolution)s)", dict(resolution='%dx%d'%resolution.xy()))
		self._screen = pygame.display.set_mode(resolution.xy(), OPENGL|DOUBLEBUF|RESIZABLE)
		pygame.display.set_caption('yamosg')

		self.log.debug("OpenGL setup (version=\"%(version)s\", vendor=\"%(vendor)s\")", dict(version=glGetString(GL_VERSION), vendor=glGetString(GL_VENDOR)))
		setup_opengl()

		Client.cursor_default = pygame.cursors.arrow
		Client.cursor_capture = pygame.cursors.diamond
		
		self._resolution = resolution
		self._split = split
		self._running = False
		self._state = StateManager()
		self._game = GameWidget(self, resolution)
		self._container = Composite(Vector2i(0,0), resolution, children=[self._game])
		self._toolbar = Toolbar()
		self._window = VBox()
		self._window.add(self._toolbar, size=LayoutAttachment(Vector2i(1,0), Vector2i(0,25)))
		self._window.add(self._container)
		self._state.push(GameState(resolution, self._window))
		self._network = Network(self, host, port)
		self._command_store = {}
		self._command_queue = []
		self._command_lock = threading.Lock()
		self._playerid = None
		self._players = {}
		self._capture_position = None

		# resizing must be done after state has been created so the event is propagated proper.
		self._resize(resolution)
	
	def add_window(self, win):
		self._container.add(win)
	
	@event(pygame.QUIT)
	def quit(self, event=None):
		self._running = False
	
	def is_running(self):
		return self._running	

	def resolution(self):
		return self._resolution

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
	
	@event(pygame.VIDEORESIZE, lambda event: Vector2i(event.w, event.h))
	def _resize(self, resolution):
		self.log.debug("Resolution changed to %dx%d", resolution.x, resolution.y)
		self._screen = pygame.display.set_mode(resolution.xy(), OPENGL|DOUBLEBUF|RESIZABLE)
		setup_opengl()

		self._resolution = resolution
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, resolution.x, 0, resolution.y, -1.0, 1.0);
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self._state.resize(resolution)
		self._game.on_resize(resolution, True)
	
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
		global event_table
		for event in pygame.event.get():
			func, adapter = event_table.get(event.type, (None,None))
			if func is None:
				continue
			func(self, adapter(event))

	@event(pygame.MOUSEMOTION)
	def _mousemotion(self, event):
		pos = Vector2i(event.pos)
		pos.y = self._resolution.y - pos.y
		self._state.on_mousemove(pos)
	
	@event(pygame.MOUSEBUTTONDOWN)
	def _mousebuttondown(self, event):
		pos = Vector2i(event.pos)
		pos.y = self._resolution.y - pos.y

		if self._capture_position is not None:
			if event.button == 1:
				callback, args, kwargs = self._capture_position
				try:
					callback(pos, *args, **kwargs)
				except:
					traceback.print_exc()
					
			self._capture_position = None
			pygame.mouse.set_cursor(*Client.cursor_default)
			return
		self._state.on_buttondown(pos, event.button)

	@event(pygame.MOUSEBUTTONUP)
	def _mousebuttonup(self, event):
		pos = Vector2i(event.pos)
		pos.y = self._resolution.y - pos.y
		self._state.on_buttonup(pos, event.button)
	
	def _render(self):
		glClearColor(1,0,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self._state.render()
		
		pygame.display.flip()
	
	def _dispatch(self, cmd, args):
		""" Run command """
		global network_log
		network_log.debug('got %s(%s)', cmd, ', '.join([str(x) for x in args]))
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
	
	@server_call('LIST_OF_ENTITIES', decode=True)
	def list_of_entities(self, descriptions):
		self._game.set_entities([Entity(**x) for x in descriptions])
	
	@server_call('ENTINFO', 'id', decode=True)
	def entity_info(self, info):
		return info

	@server_call('ENTACTION', 'id', 'action', decode=True)
	def entity_action(self, info):
		return info

	@server_call('PLAYERINFO', 'id', decode=True)
	def playerinfo(self, info):
		self._toolbar.set_cash(info['cash'])
	
	@server_call('LOGIN', 'username', 'password', decode=True)
	def login(self, info):
		self.playerid = info['id']
		self.log.debug('player id is %s', self.playerid)
		self.playerinfo(self.playerid)
	
	@server_call('PLAYERS', decode=True)
	def players(self, players):
		return players

	def player_by_id(self, id):
		return self._players.get(unicode(id), None)

	@expose
	def Hello(self):
		self.call('SET', 'ENCODER', 'json')
		self.login(password='bar', username='foo')
		self._players = self.players()
		self.list_of_entities()

	@expose
	def UPDENT(self, line):
		data = json.loads(line)
		for id, info in data.items():
			game.entity_named(id).update(info)

	def capture_position(self, callback, *args, **kwargs):
		self._capture_position = (callback, args, kwargs)
		pygame.mouse.set_cursor(*Client.cursor_capture)

terminating = False
def quit(*args):
	global terminating
	if terminating:
		print >> sys.stderr, '\rGot SIGINT again, aborting.'
		sys.exit(0)
	client.quit()
	print >> sys.stderr, '\rGot SIGINT, stopping.'
	terminating = True

def run():
	if os.path.exists('client.conf'):
		logging.config.fileConfig('client.conf')

	log = Log()
	log.info('Yamosg starting (%s)', pf.system())
	pygame.display.init()
	
	client = Client()
	signal(SIGINT, quit)

	# create "superglobal" access to the client- and game instances
	__builtins__['client'] = client
	__builtins__['game'] = client._game # hack

	client.run()
	log.info('Yamosg stopping')

if __name__ == '__main__':
	run()
