#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

from OpenGL.GL import *
from copy import copy

class Window(Widget):
	def __init__(self, position, size, format=GL_RGB8, *args, **kwargs):
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		self._move = False
	
	def on_buttondown(self, pos, button):
		self._move = True
		self._moveref = pos
	
	def on_buttonup(self, pos, button):
		self._move = False
		self._moveref = None
	
	def on_mousemove(self, pos, buttons):
		if self._move:
			self.pos -= self._moveref - pos
		
	def do_render(self):
		glClearColor(0,0.5,1,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
