#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State
from ui import Button

from OpenGL.GL import *

class Game(State):
	def __init__(self, size, widget):
		State.__init__(self, size=size, root=widget)
