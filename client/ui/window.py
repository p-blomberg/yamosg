#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget
from ui._cairo import CairoWidget, ALIGN_CENTER
from common.vector import Vector2i

from OpenGL.GL import *
from copy import copy

class _Decoration(CairoWidget):
	def __init__(self, title, *args, **kwargs):
		CairoWidget.__init__(self, *args, **kwargs)
		self._title = title
		self._font = self.create_font(size=9)
		
	def do_render(self):
		cr = self.cr
		
		self.clear((0,0,0,0))
		self._layout()
		
		cr.move_to(0, 3)
		self.text(self._title, self._font, alignment=ALIGN_CENTER, width=self.width)
		
		for i, element in enumerate(['foo', 'bar', 'baz']):
			x = 15
			y = 35 + i * 20
			
			cr.set_source_rgba (0.0, 0.0, 0.0, 1.0)
			cr.new_sub_path()
			cr.arc(x, y + 7.5, 3, 0, 2*3.1415)
			cr.fill()
			
			cr.move_to(x + 10, y)
			self.text(element, self._font)
	
	def _layout(self):
		cr = self.cr
		
		radius = 20;
		degrees = 3.1415 / 180.0;
		border = 1.0
		
		# background
		cr.new_sub_path ();
		cr.line_to (self.width - border, radius + border/2)
		cr.line_to (self.width - border, self.height)
		cr.line_to (border, self.height)
		cr.line_to (border, radius + border/2)
		cr.close_path ()
		
		cr.set_source_rgba (1.0, 1.0, 1.0, 0.95)
		cr.fill()
		
		# titlebar
		cr.new_sub_path ();
		cr.arc (self.width - radius - border, radius + border/2, radius, -90 * degrees, 0 * degrees)
		cr.arc (radius + border, radius + border/2, radius, 180 * degrees, 270 * degrees)
		cr.close_path ()
		cr.set_source_rgb (0.7, 0.5, 1.0)
		cr.fill_preserve ()
		
		# border
		cr.new_sub_path ();
		cr.arc (self.width - radius - border, radius + border/2, radius, -90 * degrees, 0 * degrees)
		cr.line_to (self.width - border, self.height)
		cr.line_to (border, self.height)
		cr.arc (radius + border, radius + border/2, radius, 180 * degrees, 270 * degrees)
		cr.close_path ()
		
		cr.set_source_rgba (0.0, 1.0, 0, 1.0)
		cr.set_line_width (border*2)
		cr.stroke ()

class Window(Widget):
	def __init__(self, position, size, bordersize=1, format=GL_RGBA8, title='Unnamed window', *args, **kwargs):
		Widget.__init__(self, position, size, *args, format=format, **kwargs)
		self._bordersize = bordersize
		self._decoration = _Decoration(title, Vector2i(0,0), size)
		
		# states
		self._ref = None
		self._is_moving = False
		self._is_resizing = False
	
	def close(self):
		self.parent.remove(self)
	
	def get_children(self):
		return [self._decoration]
	
	def on_resize(self, size):
		Widget.on_resize(self, size)
		self._decoration.on_resize(size)
	
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
		
	def do_render(self):
		glClearColor(0,0.5,1,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self._decoration.display()
		#glDisable(GL_TEXTURE_2D)
		#self._render_border()
		#self._render_titlebar()
		#glEnable(GL_TEXTURE_2D)
	
	def _render_border(self):
		glBegin(GL_QUADS)
		
		
		glColor4f(1,1,1,1)
		glVertex2f(0, 0)
		glVertex2f(0, self.height)
		glVertex2f(self.width, self.height)
		glVertex2f(self.width, 0)
		
		#glColor4f(1,1,1,1)
		#glVertex2f(self._bordersize, self._bordersize)
		#glVertex2f(self._bordersize, self.height-self._bordersize)
		#glVertex2f(self.width-self._bordersize, self.height-self._bordersize)
		#glVertex2f(self.width-self._bordersize, self._bordersize)
		
		#glColor4f(1,1,1,0.5)
		#glVertex2f(self._bordersize, self._bordersize)
		#glVertex2f(self._bordersize, self.height-self._bordersize)
		#glVertex2f(self.width-self._bordersize, self.height-self._bordersize)
		#glVertex2f(self.width-self._bordersize, self._bordersize)
		
		glEnd()
	
	def _render_titlebar(self):
		glBegin(GL_QUADS)
		
		glColor4f(0,0,1,1)
		glVertex2f(self._bordersize,            self.height-self._bordersize - 20)
		glVertex2f(self._bordersize,            self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self.height-self._bordersize)
		glVertex2f(self.width-self._bordersize, self.height-self._bordersize - 20)
		
		glEnd()