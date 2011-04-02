#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import FBOWidget
from ui._cairo import CairoWidget, ALIGN_CENTER
from common.vector import Vector2i, Vector2f, Vector3
from OpenGL.GL import *
from OpenGL.GLU import *
from copy import copy

class BaseWindow:
	def __init__(self, id=None, title='Unnamed window', minsize=Vector2i(150,150)):
		self._id = id
		self._title = title
		self._minsize = minsize
		
		# states
		self._ref = None
		self._is_moving = False
		self._is_resizing = False

	def id(self):
		return self._id

	def title(self):
		return self._title
	
	def close(self):
		self.parent.remove(self)
	
	def on_buttondown(self, pos, button):
		self.parent.bring_to_front(self)

		if pos.y > self.height-self._bordersize - 20:
			if pos.x > self.width - 20:
				self.close()
				return
			
			self._is_moving = True
			self._moveref_rel = pos
			self.focus_lock()
		
		if pos.y < 20 and (pos.x < 20 or pos.x > self.width - 20):
			self._is_resizing = True
			
			self._resize_mode = 2
			if pos.x < 20:
				self._resize_mode = 1
			
			self._moveref_abs = self.pos + pos
			self._moveref_rel = pos
			self._sizeref = self.size.copy()
			self._posref = self.pos.copy()
			self.focus_lock()
	
	def on_buttonup(self, pos, button):
		if self._is_resizing:
			self.on_resize(self.size, final=True)

		self._is_moving = False
		self._is_resizing = False
		self._resize_mode = None
		self._moveref_abs = None
		self._moveref_rel = None
		self._sizeref = None
		self._posref = None
		self.focus_unlock()
	
	def on_mousemove(self, pos, buttons):
		abs = self.pos + pos

		if self._is_moving:
			self.pos -= self._moveref_rel - pos
			
		if self._is_resizing:
			delta = self._moveref_abs - abs

			# flip axis
			delta.y *= -1
			if self._resize_mode == 1:
				delta.x *= -1

			# clamp delta
			if self._sizeref.x - delta.x < self._minsize.x:
				delta.x = self._sizeref.x - self._minsize.x
			if self._sizeref.y - delta.y < self._minsize.y:
				delta.y = self._sizeref.y - self._minsize.y

			# resize
			self.size = self._sizeref - delta

			# move window
			self.pos.y = self._posref.y + delta.y
			if self._resize_mode == 1:
				self.pos.x = self._posref.x + delta.x
						
			self.on_resize(self.size, final=False)
			self.invalidate()

class WindowDecoration(CairoWidget):
	def __init__(self, size, title, *args, **kwargs):
		CairoWidget.__init__(self, Vector2i(0,0 ), size, *args, **kwargs)
		self._title = title
		self._titlefont = self.create_font(size=9)
	
	# hit constants
	TITLEBAR = 1
	CLOSE = 2
	RESIZE = 3
	def hit_test(self, point):
		# @todo invert logic

		border = 1
		if point.y > self.height- border - 20:
			if point.x > self.width - 20:
				return self.CLOSE
			return self.TITLEBAR
		
		if point.y < 20 and (point.x < 20 or point.x > self.width - 20):
			return self.RESIZE

		return None
		

	def do_render(self):
		self.render_decoration(self.cr, self.size, self._titlefont, self._title)
	
	@classmethod
	def render_decoration(cls, cr, size, font, title):
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
		
		cr.set_source_rgba (1.0, 1.0, 1.0, 0.0)
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
		
		cr.move_to(0, 3)
		cls.text(cr, title, font, alignment=ALIGN_CENTER, width=width)

# autoposition
_autopos   = Vector2i(50, 450)
_autopos_c = 50
_autopos_d = Vector2i(20, -20)

def get_autopos(size):
	global _autopos, _autopos_c, _autopos_d
	resolution = client.resolution()

	restart_cases = [
		_autopos.y + size.y > resolution.y,
		_autopos.x + size.x > resolution.x,
		_autopos.y < 0,
		_autopos.x < 0
	]

	if any(restart_cases):
		_autopos.x = _autopos_c
		_autopos.y = resolution.y - size.y
		_autopos_c += _autopos_d.x * 2

	if _autopos_c > resolution.x * 0.5:
		_autopos_c = 0

	v = _autopos.copy()
	_autopos += _autopos_d

	return v

class OpenGLWindow(BaseWindow, FBOWidget):
	def __init__(self, position, size, bordersize=1, format=GL_RGBA8, *args, **kwargs):
		if position is None:
			position = get_autopos(size)

		BaseWindow.__init__(self, **kwargs)
		FBOWidget.__init__(self, position, size, *args, format=format, **kwargs)
	
		self._bordersize = bordersize
		self._decoration = WindowDecoration(size, self.title())
	
	def get_children(self):
		return [self._decoration]
	
	def on_resize(self, size, final):
		FBOWidget.on_resize(self, size, final)
		self._decoration.on_resize(size)

class CairoWindow(BaseWindow, CairoWidget):
	def __init__(self, position, size, bordersize=1, *args, **kwargs):
		if position is None:
			position = get_autopos(size)

		BaseWindow.__init__(self, **kwargs)
		CairoWidget.__init__(self, position, size, *args, **kwargs)
		
		self._bordersize = bordersize
		self._titlefont = self.create_font(size=9)

	def render_decoration(self):
		WindowDecoration.render_decoration(self.cr, self.size, self._titlefont, self.title())

class Window(OpenGLWindow):
	def __init__(self, widget, *args, **kwargs):
		OpenGLWindow.__init__(self, *args, **kwargs)
		self._widget = widget

		# force resizing (so the child widget will get the correct size
		self.on_resize(self.size, final=True)

	def hit_test(self, point, project=True):
		if project:
			point = self.project(point)

		# perform an initial hit test to determine if the window was hit at all.
		window_hit = OpenGLWindow.hit_test(self, point, False)
		if window_hit is None:
			return None

		# check if the window decoration was hit
		if self._decoration.hit_test(point) is not None:
			return window_hit

		# check if child was hit
		child_hit = self._widget.hit_test(point, True)
		if child_hit is not None:
			return child_hit

		return window_hit

	def get_children(self):
		return [self._widget] + OpenGLWindow.get_children(self)

	def on_resize(self, size, final):
		self._widget.pos = Vector3(self._bordersize, self._bordersize)
		self._widget.size = Vector2i(self.size.x - self._bordersize*2, self.size.y - 21) # @todo must calculate titlebar height
		self._widget.on_resize(self._widget.size, final)
		OpenGLWindow.on_resize(self, size, final)

	def do_render(self):
		glClearColor(0,0,0,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		glPushMatrix()
		self._widget.display()
		glPopMatrix()

		self._decoration.display()
		

class SampleOpenGLWindow(OpenGLWindow):
	def __init__(self, *args, **kwargs):
		OpenGLWindow.__init__(self, *args, **kwargs)
		self.rquad = 0.0
	
	def do_render(self):
		glClearColor(0,0,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self._decoration.display()
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)
		
		glPushAttrib(GL_ENABLE_BIT)
		glEnable(GL_DEPTH_TEST)
		glDisable(GL_TEXTURE_2D)
		glEnable(GL_CULL_FACE)
		
		self.rquad += 0.05
		glTranslatef(0.0, 0.0, -7.0)
		glRotatef(self.rquad,1.0,1.0,1.0)
		glBegin(GL_QUADS)

		glColor3f(0.0,1.0,0.0)
		glVertex3f( 1.0, 1.0,-1.0)
		glVertex3f(-1.0, 1.0,-1.0)
		glVertex3f(-1.0, 1.0, 1.0)
		glVertex3f( 1.0, 1.0, 1.0)

		glColor3f(1.0,0.5,0.0)
		glVertex3f( 1.0,-1.0, 1.0)
		glVertex3f(-1.0,-1.0, 1.0)
		glVertex3f(-1.0,-1.0,-1.0)
		glVertex3f( 1.0,-1.0,-1.0)

		glColor3f(1.0,0.0,0.0)
		glVertex3f( 1.0, 1.0, 1.0)
		glVertex3f(-1.0, 1.0, 1.0)
		glVertex3f(-1.0,-1.0, 1.0)
		glVertex3f( 1.0,-1.0, 1.0)

		glColor3f(1.0,1.0,0.0)
		glVertex3f( 1.0,-1.0,-1.0)
		glVertex3f(-1.0,-1.0,-1.0)
		glVertex3f(-1.0, 1.0,-1.0)
		glVertex3f( 1.0, 1.0,-1.0)

		glColor3f(0.0,0.0,1.0)
		glVertex3f(-1.0, 1.0, 1.0)
		glVertex3f(-1.0, 1.0,-1.0)
		glVertex3f(-1.0,-1.0,-1.0)
		glVertex3f(-1.0,-1.0, 1.0)

		glColor3f(1.0,0.0,1.0)
		glVertex3f( 1.0, 1.0,-1.0)
		glVertex3f( 1.0, 1.0, 1.0)
		glVertex3f( 1.0,-1.0, 1.0)
		glVertex3f( 1.0,-1.0,-1.0)
		glEnd()
		
		glPopAttrib()
		
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
		self.invalidate()

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
		
		CairoWidget.clear(cr, (0,0,0,0))
		self.render_decoration()
		
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

