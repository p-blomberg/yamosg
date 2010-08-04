#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

from OpenGL.GL import *
from copy import copy

class Window(Widget):
	def __init__(self, position, size, bordersize=1, format=GL_RGBA8, *args, **kwargs):
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		self._bordersize = bordersize
		self._move = False
	
	def on_buttondown(self, pos, button):
		if pos.y > self.height-self._bordersize - 20:
			self._move = True
			self._moveref = pos
	
	def on_buttonup(self, pos, button):
		self._move = False
		self._moveref = None
	
	def on_mousemove(self, pos, buttons):
		if self._move:
			self.pos -= self._moveref - pos
		
	def do_render(self):
		glClearColor(0,0.5,1,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self._render_border()
		self._render_titlebar()
	
	def _render_border(self):
		glBegin(GL_QUADS)
		
		glColor4f(1,0,1,1)
		glVertex2f(0, 0)
		glVertex2f(0, self.height)
		glVertex2f(self.width, self.height)
		glVertex2f(self.width, 0)
		
		glColor4f(1,1,1,1)
		glVertex2f(self._bordersize, self._bordersize)
		glVertex2f(self._bordersize, self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self._bordersize)
		
		glColor4f(1,1,1,0.5)
		glVertex2f(self._bordersize, self._bordersize)
		glVertex2f(self._bordersize, self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self._bordersize)
		
		glEnd()
	
	def _render_titlebar(self):
		glBegin(GL_QUADS)
		
		glColor4f(0,0,1,1)
		glVertex2f(self._bordersize,            self.height-self._bordersize - 20)
		glVertex2f(self._bordersize,            self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self.height-self._bordersize - 20)
		
		glEnd()