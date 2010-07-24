#!/usr/bin/python
# -*- coding: utf-8 -*-

class Widget:
	def __init__(self, pos, size):
		self.pos = pos
		self.size = size
		self.width, self.height = size.xy()
	
	def render(self):
		raise NotImplementedError

from button import Button
