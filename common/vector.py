#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

class Vector:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		try:
			# try to unpack 'x' as a tuple
			# allows us to convert a tuple to vector.
			self.x, self.y, self.z = x
		except:
			self.x = float(x)
			self.y = float(y)
			self.z = float(z)

	def tuple(self):
		return (self.x, self.y, self.z)

	def __add__(self, rhs):
		return Vector(self.x + rhs.x, self.y + rhs.y, self.z+rhs.z)

	def __sub__(self, rhs):
		return Vector(self.x - rhs.x, self.y - rhs.y, self.z+rhs.z)
	
	# scalar multiplication
	def __mul__(self, scalar):
		return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

	def __repr__(self):
		return '<vector %s, %s, %s>' % (str(self.x), str(self.y), str(self.z))

	def length_squared(self):
		return self.x*self.x + self.y*self.y + self.z*self.z
	
	def length(self):
		return math.sqrt(self.length_squared())
	
	def normalize(self):
		len = self.length()
		return Vector(self.x / len, self.y / len, self.z / len)
