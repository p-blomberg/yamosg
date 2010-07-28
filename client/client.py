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
from common.command import parse, parse_tokens, Command
from common.vector import Vector
import common.rect
from state import Initial, StateManager
from entity import Entity
from ui import Widget
from state.game import Game as GameState

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import json

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

class Game(Widget):
	def __init__(self, size):
		Widget.__init__(self, Vector(0,0,0), size)
		self.entities = []
		self._scale = 1.0
		self._rect = common.rect.Rect(0,0,0,0)
		self._panstart = None # position where the panning has started
		self._panref = None
		self._foo = 0.0
		
		self._background = [None, None, None]
		for i, filename in enumerate(['space_0.png', 'space_1.png', 'space_2.png']):
			self._background[i] = glGenTextures(1)
		
			fp = open('../textures/background/' + filename, 'rb')
			surface = pygame.image.load(fp).convert_alpha()
			data = pygame.image.tostring(surface, "RGBA", 0)
			
			glBindTexture(GL_TEXTURE_2D, self._background[i])
			glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glBindTexture(GL_TEXTURE_2D, 0)
		
		self._calc_view_matrix()
	
	def _calc_view_matrix(self):
		self._rect.w = self.size.x * self._scale
		self._rect.h = self.size.y * self._scale

		glPushMatrix()

		glLoadIdentity()
		glTranslate(-self._rect.x, -self._rect.y, -50 - self._scale)
		self._view = glGetDouble(GL_MODELVIEW_MATRIX)
		
		glPopMatrix()

	def _transform_position(self, pos):
		p = pos.copy()
		p.x += self._rect.x
		p.y += self._rect.y
		return p

	def _unproject(self, point, view=None):
		"""
		Unprojects a 2D viewport point to a 3D point on the plane <0,0,1,0>
		"""

		# sometimes it it prefered to use an old viewmatrix (eg while panning)
		if view is None:
			view = self._view

		# @todo GL_VIEWPORT is never changed, at least not until resizing.
		viewport = glGetInteger(GL_VIEWPORT)

		# The view is flipped, so Y must be flipped again.
		x = point.x
		y = viewport[3]-point.y # [3] is the height of the viewport

		# Get the min and max points
		min = Vector(gluUnProject(x, y, 0, view, self._projection, viewport))
		max = Vector(gluUnProject(x, y, 1, view, self._projection, viewport))

		# This is a simplification of the general line-plane intersection.
		# Since the plane normal is (0,0,1) and d=0, z is the only variable left.
		u = min.z / (min.z - max.z)
		return min + (max - min) * u

	def on_resize(self, size):
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()

		glLoadIdentity()
		gluPerspective(90.0, 1.3333, 0.1, 1000.0)
		glScalef(1, -1.0, 1);
		self._projection = glGetDouble(GL_PROJECTION_MATRIX)
		glPopMatrix()

		glMatrixMode(GL_MODELVIEW)

	def on_buttondown(self, pos, button):
		# transform position by camera
		world_pos = self._unproject(pos)

		if button == 1:
			for e in self.entities:
				if world_pos.x < e.position.x or world_pos.y < e.position.y:
					continue
				
				if world_pos.x > e.position.x + 50 or world_pos.y > e.position.y + 50:
					continue
				
				print e
				break
		elif button == 3:
			self.on_pan_start(pos)
		elif button == 4:
			#if self._scale > 0.2:
			self.on_zoom(-1.1)
		elif button == 5:
			self.on_zoom(1.1)

	def on_buttonup(self, pos, button):
		if button == 3:
			self.on_pan_stop(pos)
	
	def on_mousemove(self, pos, buttons):
		world_pos = self._unproject(pos)

		for e in self.entities:
			if world_pos.x < e.position.x or world_pos.y < e.position.y:
				e.hover = False
				continue
			
			if world_pos.x > e.position.x + 50 or world_pos.y > e.position.y + 50:
				e.hover = False
				continue

			e.hover = True

		if buttons[3]:
			self.on_pan_move(pos)

	#
	# Zooming
	#

	def on_zoom(self, amount):
		self._scale += amount
		self._calc_view_matrix()

	#
	# Panning
	#

	def on_pan_start(self, pos):
		self._panstart = self._unproject(pos)
		self._panref = self._rect.copy()
		self._panrefview = self._view.copy()

	def on_pan_stop(self, pos):
		pass

	def on_pan_move(self, pos):
		rel = self._unproject(pos,self._panrefview) - self._panstart
		self._rect.x = self._panref.x - rel.x
		self._rect.y = self._panref.y - rel.y
		self._calc_view_matrix()

	#
	# Rendering
	#
	
	def do_render(self):
		glClearColor(0,0,0,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self._render_background()

		# perspective projection
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadMatrixd(self._projection)
		glMatrixMode(GL_MODELVIEW)

		glDisable(GL_CULL_FACE)

		# view matrix
		glLoadIdentity()
		glMultMatrixd(self._view)

		#glTranslate(-self._rect.x, -self._rect.y, -50 - self._scale)
		#gluLookAt(0.0001,100,0,    0,0,0,   0,1,0)

		glColor4f(1,1,1,1)		
		for e in self.entities:
			glPushMatrix()
			glTranslate(e.position.x, e.position.y, e.position.z)
			
			glBindTexture(GL_TEXTURE_2D, e.sprite)

			glBegin(GL_QUADS)
			glTexCoord2f(0, 0)
			glVertex3f(0, 0, 0)
			
			glTexCoord2f(0, 1)
			glVertex3f(0, 50, 0)
			
			glTexCoord2f(1, 1)
			glVertex3f(50, 50, 0)
			
			glTexCoord2f(1, 0)
			glVertex3f(50, 0, 0)
			glEnd()

			if getattr(e, 'hover', False):
				glDisable(GL_TEXTURE_2D)
				glColor4f(1,1,0,1)
				glBegin(GL_LINE_STRIP)
				glVertex3f(0, 0, 0)
				glVertex3f(0, 50, 0)
				glVertex3f(50, 50, 0)
				glVertex3f(50, 0, 0)
				glVertex3f(0, 0, 0)
				glEnd()
				glColor4f(1,1,1,1)
				glEnable(GL_TEXTURE_2D)
			
			glPopMatrix()

		glColor(1,1,0,1)
		glutSolidSphere(5, 25, 25)
		
		# restore projection
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)

		self.invalidate()
	
	def _render_background(self):
		glPushMatrix()
		
		#glTranslate(-self._rect.x, -self._rect.y, 0.0)
		
		glColor4f(1,1,1,1)
		
		for i,s in enumerate([0.00010, 0.00007, 0.00004]):
			glBindTexture(GL_TEXTURE_2D, self._background[i])
			t = common.rect.Rect(
				self._rect.x * s,
				self._rect.y * s,
				1.0 + i * 0.4,
				1.0 + i * 0.6)

			glBegin(GL_QUADS)
			glTexCoord2f(t.x, t.y)
			glVertex2f(0, 0)
			
			glTexCoord2f(t.x, t.y + t.h)
			glVertex2f(0, self.height)
			
			glTexCoord2f(t.x + t.w, t.y + t.h)
			glVertex2f(self.width, self.height)
			
			glTexCoord2f(t.x + t.w, t.y)
			glVertex2f(self.width, 0)
			glEnd()
		
		glBindTexture(GL_TEXTURE_2D, 0)
		glPopMatrix()

class Client:
	def __init__(self, resolution=Vector(800,600), host='localhost', port=1234, split="\n"):
		# opengl must be initialized first
		self._screen = pygame.display.set_mode((int(resolution.x),int(resolution.y)), OPENGL|DOUBLEBUF|RESIZABLE)
		pygame.display.set_caption('yamosg')
		setup_opengl()
		glutInit()
		
		self._split = split
		self._running = False
		self._state = StateManager()
		self._game = Game(resolution)
		self._state.push(GameState(resolution, self._game))
		self._network = Network(self, host, port)
		self._command_store = {}
		self._command_queue = []
		self._command_lock = threading.Lock()
		self._playerid = None

		# resizing must be done after state has been created so the event is propagated proper.
		self._resize(resolution.x, resolution.y)
	
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
	
	def _resize(self, width, height):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1.0, 1.0);
		glScalef(1, -1.0, 1);
		glTranslatef(0, -height, 0);
		default_projection = glGetDouble(GL_PROJECTION_MATRIX)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self._state.resize(Vector(width, height))
	
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
				self._state.on_mousemove(Vector(event.pos))
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self._state.on_buttondown(Vector(event.pos), event.button)
			elif event.type == pygame.MOUSEBUTTONUP:
				self._state.on_buttonup(Vector(event.pos), event.button)
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
		_, self.playerid, _ = self.call('LOGIN', 'foo', 'bar')
		self.list_of_entities()
		#_, entities = self.call('LIST_OF_ENTITIES')
		#print json.loads(entities)

if __name__ == '__main__':
	pygame.display.init()
	
	client = Client()
	client.run()
