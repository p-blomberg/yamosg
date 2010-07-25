#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *

class State:
	def __init__(self, size, root=None):
		self._owner = None # will be set the StateManager
		self._root = root
		self.size = self.width, self.height = size.xy()
		
	def render(self):
		glClearColor(0,1,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		if self._root is None:
			return
		
		glPushMatrix()
		self._root.render()
		glPopMatrix()
		
		glColor4f(1,1,1,1)
		self._root.bind_texture()
		
		glBegin(GL_QUADS)
		glTexCoord2f(0, 1)
		glVertex2f(0, 0)
		
		glTexCoord2f(0, 0)
		glVertex2f(0, self.height)
		
		glTexCoord2f(1, 0)
		glVertex2f(self.width, self.height)
		
		glTexCoord2f(1, 1)
		glVertex2f(self.width, 0)
		glEnd()
		
		glBindTexture(GL_TEXTURE_2D, 0)

	def on_buttondown(self, pos, button):
		if self._root is None:
			return
		
		self._root._impl_on_buttondown(pos, button)
	
	def replace(self, state):
		return self._owner.replace(state)
	
	def push(self, state):
		return self._owner.push(state)

	def pop(self):
		return self._owner.pop()
	
class StateManager:
	def __init__(self):
		self._state = []
		
	def __getattr__(self, key):
		if key in self.__dict__:
			return self.__dict__[key]
		
		return getattr(self._state[-1], key)
	
	def replace(self, state):
		# empty state stack
		while len(self._state) > 0:
			self.pop()
		
		state._owner = self
		self._state = [state]
	
	def push(self, state):
		state._owner = self
		self._state.append(state)
	
	def pop(self):
		state = self._state.pop()
		state._owner = None

from initial import Initial
from login import Login
