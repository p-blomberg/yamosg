#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget, FBOWidget
from ui._cairo import CairoWidget
from window import BaseWindow

from OpenGL.GL import *
import inspect

class Container:
	def __init__(self, sort_key=None, children=[], *args, **kwargs):
		assert isinstance(self, Widget) or isinstance(self, CairoWidget)

		self._sort_key = sort_key
		self._children = []
		for i, child in enumerate(children):
			self.add(child, zorder=i)
		
		self.sort()

	def add(self, widget, zorder=None):
		widget.parent = self

		self._children.append(widget)
		self.invalidate()
		self.sort()

	def remove(self, widget):
		widget.parent = None
		self._children.remove(widget)
		self.invalidate()

	def get_children(self, index=None):
		if index is not None:
			return self._children[index]
		return self._children

	def sort(self):
		if self._sort_key is None:
			return

		self._children.sort(key=self._sort_key, reverse=True)

		# renumber
		n = len(self._children)
		for i,c in enumerate(self._children):
			c.__zorder = n - i

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
		
		# containers cannot be hit
		return None
