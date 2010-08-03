#!/usr/bin/python
# -*- coding: utf-8 -*-

from state import State
from ui import Button
from common.vector import Vector3

class Login(State):
	def __init__(self):
		button = Button(pos=Vector3(50,50), size=Vector3(200, 50), callback=self.login)
		State.__init__(self, root=button)

	def login(self, pos, button):
		print 'do login'
