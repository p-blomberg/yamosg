#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import FBOWidget
from container import Container
from window import BaseWindow
from OpenGL.GL import *
from copy import copy

class Composite(Container, FBOWidget):
	""" A composite container allows free-form position and sizing of its
	children. """
	
	def __init__(self, position, size, children=[], format=GL_RGB8, *args, **kwargs):
		Container.__init__(self, sort_key=lambda x: x.__zorder, children=children)
		FBOWidget.__init__(self, position, size, *args, format=format, **kwargs)

	def add(self, widget, zorder=0):
		widget.__zorder = copy(zorder)
		Container.add(self, widget)

	def bring_to_front(self, widget):
		for c in self._children:
			c.__zorder += 1
		widget.__zorder = 0
		widget.invalidate()
		self.sort()

	def find_window(self, name):
		# to make sure we dont find a window with id None
		if name is None:
			return None

		for c in self.get_children():
			if not isinstance(c, BaseWindow):
				continue

			if c.id() == name:
				return c
		return None
	
	def do_render(self):
		glClearColor(0,0.5,1,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		for x in self.get_children():
			glPushMatrix()
			x.display()
			glPopMatrix()
