#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State
from ui import Button
from common.vector import Vector

from OpenGL.GL import *

class Login(State):
	def __init__(self):
		State.__init__(self)
		self._button = Button(Vector(50,50), Vector(200, 50))
		
	def render(self):
		glClearColor(1,1,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		glPushMatrix()
		self._button.render()
		glPopMatrix()

	def on_buttondown(self, pos, button):
		print 'click', pos, button
