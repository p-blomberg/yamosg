#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State
from ui import Button
from common.vector import Vector

from OpenGL.GL import *

class Game(State):
	def __init__(self):
		State.__init__(self)
		
	def render(self):
		glClearColor(1,1,0,0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
