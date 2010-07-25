#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

from OpenGL.GL import *

class Button(Widget):
	def __init__(self, callback=None, *args, **kwargs):
		Widget.__init__(self, *args, **kwargs)
		self._callback = callback or (lambda *args: None)
	
	def on_buttondown(self, pos, button):
		self._callback(pos, button)
	
	def do_render(self):
		glTranslate(*self.pos)
		
		glColor4f(1,1,1,1)
		glBegin(GL_QUADS)
		glTexCoord2f(0, 1)
		glVertex2f(0, 0)
		
		glTexCoord2f(0, 0)
		glVertex2f(0, self.height)
		
		glTexCoord2f(1, 0)
		glVertex2f(self.width, self.height)
		
		glTexCoord2f(1, 1)
		glVertex2f(self.width, 0)
		glEnd()
