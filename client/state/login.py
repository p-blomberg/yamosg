#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State

from OpenGL.GL import *

class Login(State):
	def render(self):
		glClearColor(1,1,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	def on_buttondown(self, pos, button):
		print 'click', pos, button
