#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget
from ui._cairo import CairoWidget, ALIGN_CENTER
from common.vector import Vector2i, Vector2f
from OpenGL.GL import *
from copy import copy

class BaseWindow:
	def __init__(self, title):
		self._title = title
		
		# states
		self._ref = None
		self._is_moving = False
		self._is_resizing = False
	
	def close(self):
		self.parent.remove(self)
	
	def on_buttondown(self, pos, button):
		if pos.y > self.height-self._bordersize - 20:
			if pos.x > self.width - 20:
				self.close()
				return
			
			self._is_moving = True
			self._moveref = pos
			self.focus_lock()
		
		if pos.y < 20 and (pos.x < 20 or pos.x > self.width - 20):
			self._is_resizing = True
			
			self._resize_mode = 2
			if pos.x < 20:
				self._resize_mode = 1
			
			self._moveref = pos
			self._sizeref = self.size.copy()
			self.focus_lock()
	
	def on_buttonup(self, pos, button):
		self._is_moving = False
		self._is_resizing = False
		self._resize_mode = None
		self._moveref = None
		self._sizeref = None
		self.focus_unlock()
	
	def on_mousemove(self, pos, buttons):
		if self._is_moving:
			self.pos -= self._moveref - pos
			
		if self._is_resizing:
			delta = self._moveref - pos
			
			self.size.y += delta.y
			self.pos.y -= delta.y
			
			if self.size.y < 40:
				self.size.y = 40
			
			if self.size.x < 40:
				self.size.x = 40
				
			if self._resize_mode == 1:
				self.size.x += delta.x
				self.pos.x -= delta.x
			
			if self._resize_mode == 2:
				self.size.x -= delta.x
				#self.pos.x -= delta.x
				self._moveref.x -= delta.x
			
			self.on_resize(self.size)
			self.invalidate()

class WindowDecoration(CairoWidget):
	def __init__(self, title, *args, **kwargs):
		CairoWidget.__init__(self, Vector2i(0,0 ), size, *args, **kwargs)
		self._title = title
		self._font = self.create_font(size=9)
	
	def render(self):
		self.do_render(self.cr, self.size)
	
	@classmethod
	def do_render(cls, cr, size):
		width, height = size.xy()
		radius = 20;
		degrees = 3.1415 / 180.0;
		border = 1.0
		
		# background
		cr.new_sub_path ();
		cr.line_to (width - border, radius + border/2)
		cr.line_to (width - border, height)
		cr.line_to (border, height)
		cr.line_to (border, radius + border/2)
		cr.close_path ()
		
		cr.set_source_rgba (1.0, 1.0, 1.0, 0.95)
		cr.fill()
		
		# titlebar
		cr.new_sub_path ();
		cr.arc (width - radius - border, radius + border/2, radius, -90 * degrees, 0 * degrees)
		cr.arc (radius + border, radius + border/2, radius, 180 * degrees, 270 * degrees)
		cr.close_path ()
		cr.set_source_rgb (0.7, 0.5, 1.0)
		cr.fill_preserve ()
		
		# border
		cr.new_sub_path ();
		cr.arc (width - radius - border, radius + border/2, radius, -90 * degrees, 0 * degrees)
		cr.line_to (width - border, height)
		cr.line_to (border, height)
		cr.arc (radius + border, radius + border/2, radius, 180 * degrees, 270 * degrees)
		cr.close_path ()
		
		cr.set_source_rgba (0.0, 1.0, 0, 1.0)
		cr.set_line_width (border*2)
		cr.stroke ()

class OpenGLWindow(BaseWindow, Widget):
	def __init__(self, position, size, bordersize=1, format=GL_RGBA8, title='Unnamed window', *args, **kwargs):
		BaseWindow.__init__(self, title)
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		
		self._bordersize = bordersize
		self._decoration = WindowDecoration(title, Vector2i(0,0), size)

class CairoWindow(BaseWindow, CairoWidget):
	def __init__(self, position, size, bordersize=1, title='Unnamed window', *args, **kwargs):
		BaseWindow.__init__(self, title)
		CairoWidget.__init__(self, position, size, *args, **kwargs)
		
		self._bordersize = bordersize

class SampleCairoWindow(CairoWindow):
	def __init__(self, *args, **kwargs):
		CairoWindow.__init__(self, *args, **kwargs)
		self.points = [
			Vector2f(0.15, 0.15),
			Vector2f(0.25, 0.75),
			Vector2f(0.75, 0.25),
			Vector2f(0.85, 0.85)
		]
		self._move = None
	
	def on_buttondown(self, pos, button):
		# cairo has inverted y
		pos2 = Vector2f(pos.xy())
		pos2.y = self.height - pos2.y
		
		# absolute points
		p = [v * self.size for v in self.points]
		
		# distances
		d = [(v - pos2).length_squared() for v in p]
		for i, x in enumerate(d):
			if x < 50:
				self._move = i
				return
		
		return CairoWindow.on_buttondown(self, pos, button)
	
	def on_buttonup(self, pos, button):
		self._move = None
		return CairoWindow.on_buttonup(self, pos, button)
	
	def on_mousemove(self, pos, buttons):
		if self._move is None:
			return CairoWindow.on_mousemove(self, pos, buttons)
		
		# cairo has inverted y
		p = Vector2f(pos.xy())
		p.y = self.height - p.y
		
		p.x /= float(self.width)
		p.y /= float(self.height)
		
		self.points[self._move] = p
		self.invalidate()
	
	def do_render(self):
		cr = self.cr
		
		self.clear((0,0,0,0))
		WindowDecoration.do_render(cr, self.size)
		
		p = [v * self.size for v in self.points]
		
		cr.set_source_rgba (0., 0.0, 0.0, 1.0);
		cr.move_to (p[0].x, p[0].y);
		cr.curve_to (p[1].x, p[1].y, p[2].x, p[2].y, p[3].x, p[3].y);
		
		cr.set_line_width (10.0);
		cr.stroke ();
		
		cr.set_source_rgba (1, 0.2, 0.2, 0.6);
		cr.set_line_width (6.0);
		cr.move_to (p[0].x, p[0].y);   cr.line_to (p[1].x, p[1].y);
		cr.move_to (p[2].x, p[2].y); cr.line_to (p[3].x, p[3].y);
		cr.stroke ();

