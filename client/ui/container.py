#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

from OpenGL.GL import *
from copy import copy

class Container(Widget):
	def __init__(self, position, size, children=[], format=GL_RGB8, *args, **kwargs):
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		self._children = copy(children) # shallow copy
		
		for i, child in enumerate(children):
			self.add(child, zorder=i)
	
	def get_children(self):
		return self._children
	
	def hit_test(self, point, project=True):
		if self._focus_lock:
			return self._focus_lock, self._focus_lock.project(point)
	
		if project:
			point = self.project(point)
		
		for x in reversed(self._children):
			hit = x.hit_test(point, True)
			if hit:
				return hit
		
		return Widget.hit_test(self, point, False)
	
	def add(self, widget, zorder=0):
		widget.parent = self
		widget.__zorder = zorder
		self._children.append(widget)
		self.invalidate()
	
	def remove(self, widget):
		widget.parent = None
		self._children.remove(widget)
		self.invalidate()
	
	def do_render(self):
		glClearColor(0,0.5,1,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		for x in self._children:
			glPushMatrix()
			x.display()
			glPopMatrix()
