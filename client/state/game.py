#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State
from ui import Button
from common.vector import Vector

from OpenGL.GL import *

class Game(State):
	def __init__(self, widget):
		State.__init__(self, root=widget)
