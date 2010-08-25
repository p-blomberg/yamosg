#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import FBOWidget

from OpenGL.GL import *

class Button(FBOWidget):
	def __init__(self, callback=None, color=(1,0,0,1), *args, **kwargs):
		FBOWidget.__init__(self, *args, **kwargs)
		self._callback = callback or (lambda *args: None)
		self._color = color
	
	def on_buttondown(self, pos, button):
		self._callback(pos, button)
	
	def do_render(self):
		glClearColor(*self._color)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glTranslate(*self.pos)
		glBindTexture(GL_TEXTURE_2D, 0)
		
		glColor4f(*self._color)
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
