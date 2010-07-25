#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *

class State:
	def __init__(self, root=None):
		self._owner = None # will be set the StateManager
		self._root = root
		
	def render(self):
		glClearColor(1,1,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		if self._root is None:
			return
		
		glPushMatrix()
		self._root.render()
		glPopMatrix()

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
