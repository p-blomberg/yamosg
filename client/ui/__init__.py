#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL import extensions
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *
from common.vector import Vector2i, Vector3

class Widget:
	def __init__(self, pos=Vector3(0,0,0), size=Vector2i(1,1), **kwargs):
		self.pos = pos.copy()
		self.size = size.copy()
		self.width, self.height = size.xy()
		self.parent = None
		self._focus_lock = None
		self._invalidated = True
	
	def focus_lock(self, widget=None):
		widget = widget or self
		
		if self.parent:
			self.parent.focus_lock(widget)
		
		self._focus_lock = widget
	
	def focus_unlock(self):
		self._focus_lock = None
		
		if self.parent:
			self.parent.focus_unlock()
	
	def invalidate(self):
		self._invalidated = True

	def is_invalidated(self):
		return self._invalidated
	
	def project(self, point):
		"""
			Project a point so it is relative to the widgets space.
		"""
		return point - self.pos
	
	def get_children(self):
		"""
		Get a list of all children from this widget, only required to be
		implemented if you are doing any kind of container.
		"""
		return []
	
	def hit_test(self, point, project=True):
		"""
			Test if a point hits the object or not.
			Return the widget that is hit, or None if there is no hit at all.
		"""
		
		if self._focus_lock:
			return self._focus_lock, self._focus_lock.project(point)
		
		if project:
			point = self.project(point)
		
		if point.x < 0 or point.y < 0:
			return None
		
		if point.x > self.width or point.y > self.height:
			return None
		
		return self, point

	def on_resize(self, size, final):
		self.size = size
		self.width, self.height = size.xy()
		self.invalidate()

	def on_mousemove(self, pos, buttons):
		pass
	
	def on_buttondown(self, pos, button):
		pass
		
	def on_buttonup(self, pos, button):
		pass
	
	def _impl_on_button(self, pos, button, state):
		hit, projection = self.hit_test(pos)
		
		if hit:
			if state:
				hit.on_buttondown(projection, button)
			else:
				hit.on_buttonup(projection, button)
	
	def _impl_on_mousemove(self, pos, buttons):
		hit, projection = self.hit_test(pos)
		
		if hit:
			hit.on_mousemove(projection, buttons)
	

	def display(self):
		""" Called when the widget is suppsed to be displayed on screen. """
		raise NotImplementedError

	def render(self):
		""" Called when the widget should be redrawn (eg to cache, fbo etc) """
		raise NotImplementedError


class FBOWidget(Widget):
	def __init__(self, pos=Vector3(0,0), size=Vector2i(1,1), format=GL_RGB8, filter=GL_NEAREST, **kwargs):
		Widget.__init__(self, pos, size, **kwargs)
		self._format = format
		self._filter = filter
		self._fbo = glGenFramebuffersEXT(1)
		self._texture = glGenTextures(1)
		self._projection = self.projection()
		
		self._generate_framebuffer()
	
	def _generate_framebuffer(self):
		assert self.size.x > 0
		assert self.size.y > 0

		self.bind_fbo()
		
		glBindTexture(GL_TEXTURE_2D, self._texture)
		glTexImage2D(GL_TEXTURE_2D, 0, self._format, self.width, self.height, 0, GL_RGBA, GL_FLOAT, None)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self._filter)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self._filter)
		
		glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, self._texture, 0)
		
		glBindTexture(GL_TEXTURE_2D, 0)
		
		self.unbind_fbo()

	def on_resize(self, size, final):
		Widget.on_resize(self, size, final)
		self._projection = self.projection()
		self._generate_framebuffer()
		self.invalidate()

	def projection(self):
		glPushMatrix()
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1.0, 1.0);
		p = glGetDouble(GL_MODELVIEW_MATRIX)
		glPopMatrix()
		return p

	def bind_fbo(self):
		glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self._fbo)

	def unbind_fbo(self):
		glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

	def bind_texture(self):
		glBindTexture(GL_TEXTURE_2D, self._texture)
	
	def do_render(self):
		raise NotImplementedError

	def display(self):
		self.bind_texture()
		glColor4f(1,1,1,1)
		
		glTranslatef(self.pos.x, self.pos.y, 0.0)
		
		glBegin(GL_QUADS)
		glTexCoord2f(0, 0)
		glVertex3f(0, 0, 0)
		
		glTexCoord2f(0, 1)
		glVertex3f(0, self.height, 0)
		
		glTexCoord2f(1, 1)
		glVertex3f(self.width, self.height, 0)
		
		glTexCoord2f(1, 0)
		glVertex3f(self.width, 0, 0)
		glEnd()
	
	def render(self):
		# if any of the children are invalidated this is also invalidated.
		if any([x.is_invalidated() for x in self.get_children()]):
			self.invalidate()
	
		# must check if a child is invalidated
		if not self.is_invalidated():
			return
		
		# mark it as not invalidated before actually rendering so that widgets
		# which requires continious rendering may mark itself as invalidated.
		self._invalidated = False
		
		# First render all children
		for x in self.get_children():
			try:
				x.render()
			except:
				print 'when rendering', x, '(%s)' % x.__class__.__name__
				raise
		
		#print 'viewport:', int(self.width)
		viewport = glGetInteger(GL_VIEWPORT)
		glViewport(0, 0, int(self.width), int(self.height));
		
		# load projection
		glMatrixMode(GL_PROJECTION)
		glLoadMatrixd(self._projection)
		glMatrixMode(GL_MODELVIEW)
		
		self.bind_fbo()
		glPushMatrix()
		self.do_render()
		glPopMatrix()
		self.unbind_fbo()

		glViewport(viewport[0],
				   viewport[1],
				   viewport[2],
				   viewport[3])

from button import Button
