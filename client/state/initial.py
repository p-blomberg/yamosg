#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State
from state.login import Login

from OpenGL.GL import *

class Initial (State):
	def render(self):
		glClearColor(0,1,1,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	def on_buttondown(self, pos, button):
		self.replace(Login())
