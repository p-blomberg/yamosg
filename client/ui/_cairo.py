#!/usr/bin/python
# -*- coding: utf-8 -*-

import array, math
import cairo, pango, pangocairo
from OpenGL.GL import *
from OpenGL.GLU import *

from pango import ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT

class CairoWidget:
	def __init__(self, pos, size, format=cairo.FORMAT_ARGB32, filter=GL_NEAREST, **kwargs):
		self.pos = pos
		self.size = size
		self.width, self.height = size.xy()
		self._format = format
		self._filter = filter
		
		self._invalidated = True
		self._parent = None # @todo MERGE WITH WIDGET
		self._focus_lock = None # @todo MERGE WITH WIDGET
		
		self._generate_surface()
		
	def _generate_surface(self):
		bpp = 4

		width = int(self.width)
		height = int(self.height)
		stride = width * bpp
		self._data = array.array('c', chr(0) * stride * height)
		self.surface = cairo.ImageSurface.create_for_data(self._data, self._format, width, height, stride)
		self._texture = glGenTextures(1);
		
		self.cr = cairo.Context(self.surface)
		
		# force subpixel rendering
		self.font_options = cairo.FontOptions()
		self.font_options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		self.cr.set_font_options(self.font_options)
		
		glBindTexture(GL_TEXTURE_2D, self._texture);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self._filter)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self._filter)
	
	def bind_texture(self):
		glBindTexture(GL_TEXTURE_2D, self._texture)

	def on_mousemove(self, pos, buttons):
		pass

	def on_buttondown(self, pos, button):
		pass

	def on_buttonup(self, pos, button):
		pass

	def invalidate(self):
		self._invalidated = True

	def is_invalidated(self):
		return self._invalidated
	
	def display(self):
		self.bind_texture()
		glColor4f(1,1,1,1)
		
		glTranslatef(self.pos.x, self.pos.y, 0.0)
		
		glBegin(GL_QUADS)
		glTexCoord2f(0, 1)
		glVertex3f(0, 0, 0)
		
		glTexCoord2f(0, 0)
		glVertex3f(0, self.height, 0)
		
		glTexCoord2f(1, 0)
		glVertex3f(self.width, self.height, 0)
		
		glTexCoord2f(1, 1)
		glVertex3f(self.width, 0, 0)
		glEnd()
	
	def focus_lock(self, widget=None):
		# @todo MERGE WITH WIDGET
		widget = widget or self
		
		if self.parent:
			self.parent.focus_lock(widget)
		
		self._focus_lock = widget
	
	def focus_unlock(self):
		# @todo MERGE WITH WIDGET
		self._focus_lock = None
		
		if self.parent:
			self.parent.focus_unlock()
	
	def project(self, point):
		"""
			Project a point so it is relative to the widgets space.
		"""
		
		 # @todo MERGE WITH WIDGET
		return point - self.pos
	
	def hit_test(self, point, project=True):
		"""
			Test if a point hits the object or not.
			Return the widget that is hit, or None if there is no hit at all.
		"""
		
		# @todo This is duplicated from Widget, they should both use the same.
		#       Perhaps it would be better to create a BaseWidget and than split
		#       to OpenGL and Cairo implementations early.
		
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
		self._generate_surface()
		self._invalidated = True
		
	def do_render(self):
		raise NotImplementedError
	
	def render(self):
		if not self._invalidated:
			return
		
		self.do_render()
		glBindTexture(GL_TEXTURE_2D, self._texture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_BGRA, GL_UNSIGNED_BYTE, self._data.tostring());
		
		self._invalidated = False
	
	@classmethod
	def create_font(cls, font='Sans', size=12):
		return pango.FontDescription('%s %f' % (font, size))
	
	@classmethod
	def clear(cls, cr, color=(0,0,0,0)):
		cr.save()
		cr.set_source_rgba(*color)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.restore()
	
	@classmethod
	def text(cls, cr, text, font, color=(0,0,0,1), alignment=pango.ALIGN_LEFT, justify=False, width=None):
		cr.set_source_rgba(*color)
		
		ctx = pangocairo.CairoContext(cr)
		layout = ctx.create_layout()
		layout.set_font_description(font)
		
		if width:
			layout.set_width(int(width * pango.SCALE))
		
		layout.set_alignment(alignment)
		layout.set_justify(justify)
		
		layout.set_markup(text);
		ctx.show_layout(layout)

		return layout.get_pixel_extents()
