#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget
from ui.icon import Icon

from OpenGL.GL import *

class Label(Widget):
	def __init__(self, icon, callback=None, *args, **kwargs):
		Widget.__init__(self, *args, **kwargs)
		self._icon = icon
		self._icon.pos = self.pos
		self._callback = callback or (lambda *args: None)
	
	def on_resize(self, size, final):
		self._icon.on_resize(size, final)
		Widget.on_resize(self, size, final)

	def render(self):
		self._icon.render()

	def display(self):
		self._icon.display()

