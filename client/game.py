#!/usr/bin/python
# -*- coding: utf-8 -*-

from copy import copy, deepcopy

from ui import Widget
from common.vector import Vector
from common.rect import Rect

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

class GameWidget(Widget):
	def __init__(self, size):
		Widget.__init__(self, Vector(0,0,0), size)
		self.entities = []
		self._scale = 1.0
		self._rect = Rect(0,0,0,0)
		self._panstart = None # position where the panning has started
		self._panref = None
		self._is_panning = False
		self._foo = 0.0
		
		self._background = [None, None, None]
		for i, filename in enumerate(['space_0.png', 'space_1.png', 'space_2.png']):
			self._background[i] = glGenTextures(1)
		
			fp = open('../textures/background/' + filename, 'rb')
			surface = pygame.image.load(fp).convert_alpha()
			data = pygame.image.tostring(surface, "RGBA", 0)
			
			glBindTexture(GL_TEXTURE_2D, self._background[i])
			glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glBindTexture(GL_TEXTURE_2D, 0)
		
		self._calc_view_matrix()
	
	def _calc_view_matrix(self):
		self._rect.w = self.size.x * self._scale
		self._rect.h = self.size.y * self._scale

		glPushMatrix()

		glLoadIdentity()
		glTranslate(-self._rect.x, -self._rect.y, -50 - self._scale)
		self._view = glGetDouble(GL_MODELVIEW_MATRIX)
		
		glPopMatrix()

	def _transform_position(self, pos):
		p = pos.copy()
		p.x += self._rect.x
		p.y += self._rect.y
		return p

	def _unproject(self, point, view=None):
		"""
		Unprojects a 2D viewport point to a 3D point on the plane <0,0,1,0>
		"""

		# sometimes it it prefered to use an old viewmatrix (eg while panning)
		if view is None:
			view = self._view

		# @todo GL_VIEWPORT is never changed, at least not until resizing.
		viewport = glGetInteger(GL_VIEWPORT)

		# The view is flipped, so Y must be flipped again.
		x = point.x
		y = viewport[3]-point.y # [3] is the height of the viewport

		# Get the min and max points
		min = Vector(gluUnProject(x, y, 0, view, self._projection, viewport))
		max = Vector(gluUnProject(x, y, 1, view, self._projection, viewport))

		# This is a simplification of the general line-plane intersection.
		# Since the plane normal is (0,0,1) and d=0, z is the only variable left.
		u = min.z / (min.z - max.z)
		return min + (max - min) * u

	def projection(self):
		self._ortho_projection = Widget.projection(self)
	
		glPushMatrix()
		glLoadIdentity()
		gluPerspective(90.0, 1.3333, 0.1, 1000.0)
		glScalef(1, -1.0, 1);
		p = glGetDouble(GL_MODELVIEW_MATRIX)
		glPopMatrix()
		return p
	
	def on_buttondown(self, pos, button):
		# transform position by camera
		world_pos = self._unproject(pos)

		if button == 1:
			for e in self.entities:
				if world_pos.x < e.position.x or world_pos.y < e.position.y:
					continue
				
				if world_pos.x > e.position.x + 50 or world_pos.y > e.position.y + 50:
					continue
				
				print e
				break
		elif button == 3:
			self.on_pan_start(pos)
		elif button == 4:
			#if self._scale > 0.2:
			self.on_zoom(-1.1, pos)
		elif button == 5:
			self.on_zoom(1.1, pos)

	def on_buttonup(self, pos, button):
		if button == 3:
			self.on_pan_stop(pos)
	
	def on_mousemove(self, pos, buttons):
		world_pos = self._unproject(pos)

		for e in self.entities:
			if world_pos.x < e.position.x or world_pos.y < e.position.y:
				e.hover = False
				continue
			
			if world_pos.x > e.position.x + 50 or world_pos.y > e.position.y + 50:
				e.hover = False
				continue

			e.hover = True

		if buttons[3] and self._is_panning:
			self.on_pan_move(pos)

	#
	# Zooming
	#

	def on_zoom(self, amount, ref):
		a = self._unproject(ref)
		self._scale += amount
		self._calc_view_matrix()
		b = self._unproject(ref)

		delta = b-a
		self._rect.x -= delta.x
		self._rect.y -= delta.y
		self._calc_view_matrix()

	#
	# Panning
	#

	def on_pan_start(self, pos):
		self._is_panning = True
		self._panstart = self._unproject(pos)
		self._panref = self._rect.copy()
		self._panrefview = copy(self._view)

	def on_pan_stop(self, pos):
		self._is_panning = False

	def on_pan_move(self, pos):
		rel = self._unproject(pos,self._panrefview) - self._panstart
		self._rect.x = self._panref.x - rel.x
		self._rect.y = self._panref.y - rel.y
		self._calc_view_matrix()

	#
	# Rendering
	#
	
	def do_render(self):
		glClearColor(0,0,0,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self._render_background()

		glDisable(GL_CULL_FACE)

		# view matrix
		glLoadIdentity()
		glMultMatrixd(self._view)

		#glTranslate(-self._rect.x, -self._rect.y, -50 - self._scale)
		#gluLookAt(0.0001,100,0,    0,0,0,   0,1,0)

		glColor4f(1,1,1,1)		
		for e in self.entities:
			glPushMatrix()
			glTranslate(e.position.x, e.position.y, e.position.z)
			
			glBindTexture(GL_TEXTURE_2D, e.sprite)

			glBegin(GL_QUADS)
			glTexCoord2f(0, 0)
			glVertex3f(0, 0, 0)
			
			glTexCoord2f(0, 1)
			glVertex3f(0, 50, 0)
			
			glTexCoord2f(1, 1)
			glVertex3f(50, 50, 0)
			
			glTexCoord2f(1, 0)
			glVertex3f(50, 0, 0)
			glEnd()

			if getattr(e, 'hover', False):
				glDisable(GL_TEXTURE_2D)
				glColor4f(1,1,0,1)
				glBegin(GL_LINE_STRIP)
				glVertex3f(0, 0, 0)
				glVertex3f(0, 50, 0)
				glVertex3f(50, 50, 0)
				glVertex3f(50, 0, 0)
				glVertex3f(0, 0, 0)
				glEnd()
				glColor4f(1,1,1,1)
				glEnable(GL_TEXTURE_2D)
			
			glPopMatrix()

		self.invalidate()
	
	def _render_background(self):
		# render background in an orthogonal projection
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadMatrixd(self._ortho_projection)
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		
		glColor4f(1,1,1,1)
		
		for i,s in enumerate([0.00010, 0.00007, 0.00004]):
			glBindTexture(GL_TEXTURE_2D, self._background[i])
			t = Rect(
				self._rect.x * s,
				self._rect.y * s,
				1.0 + i * 0.4,
				1.0 + i * 0.6)
			glBegin(GL_QUADS)
			glTexCoord2f(t.x, t.y)
			glVertex2f(0, 0)
			
			glTexCoord2f(t.x, t.y + t.h)
			glVertex2f(0, self.height)
			
			glTexCoord2f(t.x + t.w, t.y + t.h)
			glVertex2f(self.width, self.height)
			
			glTexCoord2f(t.x + t.w, t.y)
			glVertex2f(self.width, 0)
			glEnd()
		
		
		glBindTexture(GL_TEXTURE_2D, 0)
		
		# restore matrices
		glPopMatrix()
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)