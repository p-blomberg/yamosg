#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget, FBOWidget
from window import BaseWindow

from OpenGL.GL import *
from copy import copy
import inspect

class Container:
	def __init__(self, sort_key, children=[], *args, **kwargs):
		assert isinstance(self, Widget)

		self._sort_key = sort_key
		self._children = []
		for i, child in enumerate(children):
			self.add(child, zorder=i)
		
		self.sort()

	def add(self, widget):
		widget.parent = self

		self._children.append(widget)
		self.invalidate()
		self.sort()

	def remove(self, widget):
		widget.parent = None
		self._children.remove(widget)
		self.invalidate()

	def get_children(self):
		return self._children

	def bring_to_front(self, widget):
		for c in self._children:
			c.__zorder += 1
		widget.__zorder = 0
		self.sort()

	def sort(self):
		self._children.sort(key=self._sort_key, reverse=True)

		# renumber
		n = len(self._children)
		for i,c in enumerate(self._children):
			c.__zorder = n - 1

	def is_invalidated(self):
		return any([x.is_invalidated() for x in self.get_children()])

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

class Composite(Container, FBOWidget):
	def __init__(self, position, size, children=[], format=GL_RGB8, *args, **kwargs):
		Container.__init__(self, sort_key=lambda x: x.__zorder, children=children)
		FBOWidget.__init__(self, position, size, *args, format=format, **kwargs)

	def add(self, widget, zorder=0):
		widget.__zorder = zorder
		Container.add(self, widget)

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
