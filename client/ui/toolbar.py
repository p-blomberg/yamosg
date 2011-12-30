#!/usr/bin/python
# -*- coding: utf-8 -*-

from _cairo import CairoWidget, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT
from common.vector import Vector2i
import cairo

class Toolbar(CairoWidget):
	def __init__(self, game):
		CairoWidget.__init__(self, Vector2i(0,0), Vector2i(1,1), format=cairo.FORMAT_RGB24)
		self.font = self.create_font()
		self.game = game
		self.cash = 0

	def do_render(self):
		self.clear(self.cr, (1,1,1,1))
		self.cr.identity_matrix()
		self.cr.translate(0, 4)

		# positional information
		self.cr.move_to(5, 0)
		self.text(self.cr, "%.1f %.1f " % self.game.position()[:2], self.font)

		# player info
		self.cr.move_to(self.width-205, 0)
		self.text(self.cr, 'Money: %d' % self.cash, self.font, alignment=ALIGN_RIGHT, width=200)

	def set_cash(self, cash):
		self.cash = cash
		self.invalidate()
