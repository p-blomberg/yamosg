#!/usr/bin/python
# -*- coding: utf-8 -*-

class State:
	def __init__(self):
		self._owner = None # will be set the StateManager
		
	def render(self):
		raise NotImplementedError

	def on_buttondown(self, pos, button):
		raise NotImplementedError
	
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
