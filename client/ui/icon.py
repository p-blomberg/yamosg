#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget

import pygame
import traceback
import os, os.path
from OpenGL.GL import *
import rsvg_wrapper as rsvg
import array
import cairo
import resources

class Icon(Widget):
	def __init__(self, filename):
		Widget.__init__(self)
		
		self._filename = resources.realpath(filename)
		(self._texture, real_size) = self.load_texture(self._filename)
	
	def on_resize(self, size, final):
		Widget.on_resize(self, size, final)
		if final and self._filename[-4:] == '.svg':
			self._texture,_ = self._rasterize_svg(self._filename)
	
	def load_texture(self, file):
		if file[-4:] == '.svg':
			return self._rasterize_svg(file)
		
		texture = glGenTextures(1)
		
		try:
			surface = pygame.image.load(open(file, 'rb')).convert_alpha()
		except:
			traceback.print_exc()
			fp = resources.open('data/default_texture.png', 'rb')
			surface = pygame.image.load(fp).convert_alpha()
		
		try:
			data = pygame.image.tostring(surface, "RGBA", True)
			
			glBindTexture(GL_TEXTURE_2D, texture)
			glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		except Exception, e:
			traceback.print_exc()
		
		return (texture, surface.get_size())
	
	def _rasterize_svg(self, file):
		svg = rsvg.Handle(file)
		real_size = svg.get_dimension_data()
		
		s = self.size

		if s[0] == -1 and s[0] == -1:
			scale = (1.0, 1.0)
		elif s[0] == -1:
			r = float(s[1]) / real_size[1]
			scale = (r, r)
		elif s[1] == -1:
			r = float(s[0]) / real_size[0]
			scale = (r, r)
		else: # non uniform
			scale = (float(s[0]) / real_size[0], float(s[1]) / real_size[1])
			
		(width, height) = size = (int(real_size[0] * scale[0]), int(real_size[1] * scale[1]))

		
		data = array.array('c', chr(0) * width * height * 4)
		stride = width * 4
		
		surface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, width, height, stride)
		texture = glGenTextures(1);
		
		cr = cairo.Context(surface)			
		cr.translate(0, height)
		cr.scale(scale[0], -scale[1])
		svg.render_cairo(cr)
		
		glBindTexture(GL_TEXTURE_2D, texture);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		
		glBindTexture(GL_TEXTURE_2D, texture);
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, data.tostring());
		
		return (texture, size)

	def display(self):
		glBindTexture(GL_TEXTURE_2D, self._texture);
		glColor4f(1,1,1,1)
		
		glTranslatef(self.pos.x, self.pos.y, 0.0)
		
		glBegin(GL_QUADS)
		glTexCoord2f(0, 0)
		glVertex3f(0, 0, 0)
		
		glTexCoord2f(0, 1)
		glVertex3f(0, self.height, 0)
		
		glTexCoord2f(1, 1)
		glVertex3f(self.width, self.height, 0)
		
		glTexCoord2f(1, 0)
		glVertex3f(self.width, 0, 0)
		glEnd()

	def render(self):
		pass
