#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *

class State:
	def __init__(self, size, root=None):
		self._owner = None # will be set the StateManager
		self._root = root
		self.size = self.width, self.height = size.xy()
		self.button = [False] * 12 # assume 12 buttons @todo query or something
	
	def resize(self, size):
		self.size = self.width, self.height = size.xy()
		self._root.on_resize(size, final=True)

	def render(self):
		glClearColor(0,1,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		if self._root is None:
			return
		
		# store matrices
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		
		# render root UI element
		self._root.render()
		
		# restore matrices
		glPopMatrix()
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
		# display root UI element
		self._root.display()
		
		glBindTexture(GL_TEXTURE_2D, 0)

	def on_buttondown(self, pos, button):
		self.button[button] = True
		self._root._impl_on_button(pos, button, True)
	
	def on_buttonup(self, pos, button):
		self.button[button] = False
		self._root._impl_on_button(pos, button, False)
	
	def on_mousemove(self, pos):
		self._root._impl_on_mousemove(pos, self.button)
	
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
