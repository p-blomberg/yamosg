#!/usr/bin/python
# -*- coding: utf-8 -*-

from _cairo import CairoWidget, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT
from common.vector import Vector2i
import cairo

class Toolbar(CairoWidget):
	def __init__(self):
		CairoWidget.__init__(self, Vector2i(0,0), Vector2i(1,1), format=cairo.FORMAT_RGB24)
		self.font = self.create_font()
		self.cash = 0

	def do_render(self):
		self.clear(self.cr, (1,1,1,1))
		self.cr.move_to(self.width-205, 5)
		self.text(self.cr, 'Money: %d' % self.cash, self.font, alignment=ALIGN_RIGHT, width=200)

	def set_cash(self, cash):
		self.cash = cash
		self.invalidate()
