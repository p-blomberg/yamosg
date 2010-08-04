#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

from OpenGL.GL import *
from copy import copy

class Window(Widget):
	def __init__(self, position, size, bordersize=1, format=GL_RGBA8, *args, **kwargs):
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		self._bordersize = bordersize
		
		# states
		self._ref = None
		self._is_moving = False
		self._is_resizing = False
	
	def on_buttondown(self, pos, button):
		if pos.y > self.height-self._bordersize - 20:
			self._is_moving = True
			self._moveref = pos
			self.focus_lock()
		
		if pos.y < 20 and (pos.x < 20 or pos.x > self.width - 20):
			self._is_resizing = True
			
			self._resize_mode = 2
			if pos.x < 20:
				self._resize_mode = 1
			
			self._moveref = pos
			self._sizeref = self.size.copy()
			self.focus_lock()
	
	def on_buttonup(self, pos, button):
		self._is_moving = False
		self._is_resizing = False
		self._resize_mode = None
		self._moveref = None
		self._sizeref = None
		self.focus_unlock()
	
	def on_mousemove(self, pos, buttons):
		if self._is_moving:
			self.pos -= self._moveref - pos
			
		if self._is_resizing:
			delta = self._moveref - pos
			
			self.size.y += delta.y
			self.pos.y -= delta.y
			
			if self.size.y < 40:
				self.size.y = 40
			
			if self.size.x < 40:
				self.size.x = 40
				
			if self._resize_mode == 1:
				self.size.x += delta.x
				self.pos.x -= delta.x
			
			if self._resize_mode == 2:
				self.size.x -= delta.x
				#self.pos.x -= delta.x
				self._moveref.x -= delta.x
			
			self.on_resize(self.size)
			self.invalidate()
		
	def do_render(self):
		glClearColor(0,0.5,1,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		glDisable(GL_TEXTURE_2D)
		self._render_border()
		self._render_titlebar()
		glEnable(GL_TEXTURE_2D)
	
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