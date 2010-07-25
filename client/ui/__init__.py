#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL import extensions
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *

class Widget:
	def __init__(self, pos, size, format=GL_RGBA32F, filter=GL_NEAREST):
		self.pos = pos
		self.size = size
		self.width, self.height = size.xy()
		
		self._fbo = glGenFramebuffers(1)
		self._texture = glGenTextures(1)
		self._invalidated = True
		
		self.bind_fbo()
		
		glBindTexture(GL_TEXTURE_2D, self._texture)
		glTexImage2D(GL_TEXTURE_2D, 0, format,  self.width, self.height, 0, GL_RGBA, GL_FLOAT, None)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
		
		glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, self._texture, 0)
		
		self.unbind_fbo()
	
	def bind_fbo(self):
		glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self._fbo)

	def unbind_fbo(self):
		glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

	def bind_texture(self):
		glBindTexture(GL_TEXTURE_2D, self._texture)

	def invalidate(self):
		self._invalidated = True
	
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
	
	def on_buttondown(self, pos, button):
		pass
	
	def _impl_on_buttondown(self, pos, button):
		projection = self.project(pos)
		hit = self.hit_test(projection, False)
		
		if hit:
			self.on_buttondown(projection, button)
	
	def do_render(self):
		raise NotImplementedError
	
	def render(self):
		if not self._invalidated:
			return
		
		# mark it as not invalidated before actually rendering so that widgets
		# which requires continious rendering may mark itself as invalidated.
		self._invalidated = False
		
		self.bind_fbo()
		self.do_render()
		self.unbind_fbo()

from button import Button
