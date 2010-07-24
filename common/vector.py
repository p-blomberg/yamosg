#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

class Vector:
	def __init__(self, x=0, y=0):
		try:
			# try to unpack 'x' as a tuple
			# allows us to convert a tuple to vector.
			self.x, self.y = x
		except:
			self.x = x
			self.y = y

	def tuple(self):
		return (self.x, self.y)

	def __add__(self, rhs):
		return Vector(self.x + rhs.x, self.y + rhs.y)

	def __sub__(self, rhs):
		return Vector(self.x - rhs.x, self.y - rhs.y)
	
	# scalar multiplication
	def __mul__(self, scalar):
		return Vector(self.x * scalar, self.y * scalar)

	def __repr__(self):
		return '<vector %s, %s>' % (str(self.x), str(self.y))

	def length_squared(self):
		return self.x*self.x + self.y*self.y
	
	def length(self):
		return math.sqrt(self.length_squared())
	
	def normalize(self):
		len = self.length()
		return Vector(self.x / len, self.y / len)
