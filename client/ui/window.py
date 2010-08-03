#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

from OpenGL.GL import *
from copy import copy

class Window(Widget):
	def __init__(self, position, size, children=[], format=GL_RGB8, *args, **kwargs):
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		self._children = copy(children) # shallow copy
	
	def get_children(self):
		return self._children
	
	def hit_test(self, point, project=True):
		if project:
			point = self.project(point)
		
		for x in self._children:
			hit = x.hit_test(point, False)
			if hit:
				return hit
		
		return Widget.hit_test(point, False)
	
	def do_render(self):
		glClearColor(0,0.5,1,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		for x in self._children:
			glPushMatrix()
			x.display()
			glPopMatrix()
