#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget
from ui.container import Container
from ui._cairo import CairoWidget
from common.vector import Vector3, Vector2i
from OpenGL.GL import *
from pango import ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT

class TabView(Container, CairoWidget):
	tab_bar_height = 25
	tab_space = 15 # space between tabs

	def __init__(self, position=Vector3(0,0,0), size=Vector2i(1,1), tabs=[], **kwargs):
		for x in tabs:
			if not isinstance(x, Tab):
				raise ValueError, 'TabView can only contain Tabs, not %s', type(x)
			
		self._children = [x.widget for x in tabs]
		self._titles = [x.title for x in tabs]

		Container.__init__(self, children=self._children)
		CairoWidget.__init__(self, position, size, **kwargs)
		
		self._font = self.create_font(size=9)
		self._selected = 0

	def get_active_child(self):
		return self.get_children(self._selected)
	
	def on_mousemove(self, pos, buttons):
		pass
			
	def on_buttonup(self, pos, button):
		pass

	def on_buttondown(self, pos, button):
		w = self.size.x / len(self.get_children())
		self._selected = pos.x / w
		self.invalidate()

	def on_resize(self, size, *args, **kwargs):
		CairoWidget.on_resize(self, size, *args, **kwargs)
		
		childsize = Vector2i(size[0], size[1]-self.tab_bar_height)
		for widget in self.get_children():
			widget.on_resize(childsize, *args, **kwargs)

	def hit_test(self, point, project=True):
		# cairo has inverted y
		p = Vector2i(point.xy())
		p.y = self.height - p.y

		if p.y < self.tab_bar_height:
			return self, point

		return self.get_active_child().hit_test(point, project)

	def do_render(self):
		self.clear(self.cr, color=(1,0,1,1))

		w = self.size.x / len(self.get_children())
		for i, title in enumerate(self._titles):
			self.cr.save()
			
			self.cr.rectangle(w*i,0,w*i+w,self.tab_bar_height)
			if i == self._selected:
				self.cr.set_source_rgba(0,1,1,1)
			else:
				self.cr.set_source_rgba(1,1,0,1)
			self.cr.fill_preserve()
			self.cr.set_source_rgba(0,0,0,1)
			self.cr.stroke()

			self.cr.move_to(w*i, 5)
			self.text(self.cr, title, self._font, width=w, alignment=ALIGN_CENTER)

			self.cr.restore()

	def render(self):
		CairoWidget.render(self)
		for x in self.get_children():
			glPushMatrix()
			x.render()
			glPopMatrix()

	def display(self):
		glTranslatef(*self.pos)
		CairoWidget.display(self)

		glPushMatrix()
		self.get_active_child().display()
		glPopMatrix()

class Tab:
	def __init__(self, title, widget):
		self.title = title
		self.widget = widget
