#!/usr/bin/python
# -*- coding: utf-8 -*-

class Widget:
	def __init__(self, pos, size):
		self.pos = pos
		self.size = size
		self.width, self.height = size.xy()
	
	def project(self, point):
		"""
			Project a point so it is relative to the widgets space.
		"""
		return point - self.pos
	
	def hit_test(self, point, project=True):
		"""
			Test if a point hits the object or not.
			Return the widget that is hit, or None if there is no hit at all.
		"""
		
		if project:
			point = self.project(point)
		
		if point.x < 0 or point.y < 0:
			return None
		
		if point.x > self.width or point.y > self.height:
			return None
		
		return self
	
	def render(self):
		raise NotImplementedError

from button import Button
