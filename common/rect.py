#!/usr/bin/python
# -*- coding: utf-8 -*-

class Rect:
	def __init__(self, x, y, w, h):
		self.x = float(x)
		self.y = float(y)
		self.w = float(w)
		self.h = float(h)

	def copy(self):
		return Rect(self.x, self.y, self.w, self.h)

	def __str__(self):
		return '<Rect (%.3f %.3f %.3f %.3f)>' % (self.x, self.y, self.w, self.h)
