#!/usr/bin/python
# -*- coding: utf-8 -*-

from copy import copy, deepcopy

from ui import FBOWidget
from ui.button import Button
from ui.box import HBox, VBox
from ui.grid import Grid
from ui.window import Window
from ui.layout import LayoutAttachment
from ui.icon import Icon
from ui._cairo import CairoWidget, ALIGN_RIGHT
from ui.tabview import TabView, Tab
from common.vector import Vector2i, Vector2f, Vector3
from common.rect import Rect

import pygame, cairo, os.path
from OpenGL.GL import *
from OpenGL.GLU import *
import types, traceback
import functools
import common.resources as resources

def load(path):
	return cairo.ImageSurface.create_from_png(os.path.join('../textures', path))

type_icon = {
	'Station': 'textures/icon/gateway.png',
	'Miner': 'textures/icon/miner.png',
}

MIN_SIZE_THRESHOLD = 15

_ACTION_LUT = {}
class EntityWindow(Window):
	def action(name, icon):
		global _ACTION_LUT
		def wrapper(func):
			_ACTION_LUT[name] = (icon, func)
			return func
		return wrapper


	#	'LOAD':  ('BTNLoad.png', EntityWindow.on_load),
	#	'BUILD': ('BTNHumanBuild.png', EntityWindow.on_build)
	#}

	def __init__(self, entity, info, **kwargs):
		global _ACTION_LUT
		title = str(entity.id)
		if entity.owner:
			title += ' (%s)' % entity.owner

		actions = info['actions']
		act = []
		tabs = []

		if 'MOVE' in actions:
			act.append(Button(Icon(filename='textures/tiger.svg'), 
				functools.partial(EntityWindow.on_move, self)
			))

		if len(act) > 0:
			grid = Grid(3, 3, *act)
			tabs.append(Tab('Act', grid))

		if 'BUILD' in actions:
			build = []
			for type in info['Buildlist']:
				callback = functools.partial(EntityWindow.on_build, self, what=type)
				build.append(Button(Icon(filename=type_icon.get(type, 'textures/tiger.svg')), callback=callback))
			grid = Grid(3, 3, *build)
			tabs.append(Tab('Build', grid))

		if 'SET_CARGO_TYPE' in actions:
			cargo_types = []
			for type in info['Cargo_type_list']:
				callback = functools.partial(EntityWindow.on_set_cargo_type, self, what=type)
				cargo_types.append(Button(Icon(filename='textures/tiger.svg'), callback=callback))
			grid = Grid(3, 3, *cargo_types)
			tabs.append(Tab('Set cargo type', grid))
		
		tabs.append(Tab('Stats', EntityStats(info)))
		tab = TabView(tabs=tabs)

		Window.__init__(self, widget=tab, position=None, size=Vector2i(300,200), id=entity.id, title=title, **kwargs)
		self._entity = entity
		self._info = info

	def on_move(self, pos, button):
		def callback(p):
			p = game.unproject(p)
			client.entity_action(id=self._entity.id, action='MOVE', varargs=(p.x, p.y, p.z))
		client.capture_position(callback=callback)

	def on_build(self, pos, button, what):
		try:
			info = client.entity_action(self._entity.id, 'BUILD', varargs=(what,))
		except RuntimeError, e:
			print e

	def on_set_cargo_type(self, pos, button, what):
		try:
			info = client.entity_action(self._entity.id, 'SET_CARGO_TYPE', varargs=(what,))
		except RuntimeError, e:
			print e

class EntityStats(CairoWidget):
	def __init__(self, info):
		CairoWidget.__init__(self, Vector2i(0,0), Vector2i(1,1))
		info['Minable'] and 'Yes' or 'No'
		info['Cargo'] = ', '.join(['%s:%d' % (x['Type'],y) for x,y in info['Cargo']])
		self._info = info
		self._font = self.create_font('Monospace')

	def do_render(self):
		cr = self.cr
		self.clear(cr, (1,0,0,1))

		text = ''
		for k, v in self._info.items():
			text += "%-11s: %s\n" % (k,v)

		cr.move_to(5,0)
		self.text(cr, text, self._font)
	
class GameWidget(FBOWidget):
	def __init__(self, client, size):
		FBOWidget.__init__(self, Vector2i(0,0), size)
		self._client = client
		self._entities = {}
		self._selection = [] # current selected entities
		self._scale = 1.0
		self._camera = Vector3(0,0,50)
		self._rect = Rect(0,0,0,0)
		self._panstart = None # position where the panning has started
		self._panref = None
		self._is_panning = False
		self._is_selecting = False

		# cannot use numpy directly as it might not be available on stupid OSs (OSX, I'm looking at you!)
		self._viewport = glGetInteger(GL_VIEWPORT)
		self._viewport[0] = 0
		self._viewport[1] = 0
		self._viewport[2] = 0
		self._viewport[3] = 0
		
		self._background = [None, None, None]
		for i, filename in enumerate(['space_0.png', 'space_1.png', 'space_2.png']):
			self._background[i] = glGenTextures(1)
		
			fp = resources.open(('textures/background', filename), 'rb')
			surface = pygame.image.load(fp).convert_alpha()
			data = pygame.image.tostring(surface, "RGBA", 0)
			
			glBindTexture(GL_TEXTURE_2D, self._background[i])
			glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glBindTexture(GL_TEXTURE_2D, 0)
		
		self._calc_view_matrix()

	def set_entities(self, entities):
		self._entities = {}
		for e in entities:
			self._entities[e.id] = e
			e.__selected = False

	def add_entity(self, entity):
		self._entities[entity.id] = entity
		entity.__selected = False

	def entity_named(self, key):
		return self._entities[key]

	def position(self):
		return self._camera.xyz()

	def _calc_view_matrix(self):
		""" Calculates a new view-matrix and the boundary of the z-plane. """
		
		glPushMatrix()
		glLoadIdentity()
		glTranslate(-self._camera.x, -self._camera.y, -self._camera.z)
		self._view = glGetDouble(GL_MODELVIEW_MATRIX)
		glPopMatrix()

		# minor hack, if the viewport hasn't been setup yet we cannot determine
		# the z-plane yet.
		if self._viewport[2] == 0:
			return

		min = self.unproject(Vector2i(0,0))
		max = self.unproject(self.size)
		self._rect.x = min.x
		self._rect.y = max.y
		self._rect.w = max.x - min.x
		self._rect.h = min.y - max.y

	def _transform_position(self, pos):
		p = pos.copy()
		p.x += self._camera.x
		p.y += self._camera.y
		return p

	def unproject(self, point, view=None):
		"""
		Unprojects a 2D viewport point to a 3D point on the plane <0,0,1,0>
		"""

		# sometimes it it prefered to use an old viewmatrix (eg while panning)
		if view is None:
			view = self._view

		# @todo GL_VIEWPORT is never changed, at least not until resizing.
		#viewport = glGetInteger(GL_VIEWPORT)
		#print viewport, self._viewport

		# The view is flipped, so Y must be flipped again.
		# NO YOU!!
		x = point.x
		y = point.y
		#y = viewport[3]-point.y # [3] is the height of the viewport

		self._viewport[3] = 600
		#print x,y, self._viewport
		# Get the min and max points

		min = Vector3(gluUnProject(x, y, 0, view, self._projection, self._viewport))
		max = Vector3(gluUnProject(x, y, 1, view, self._projection, self._viewport))

		# This is a simplification of the general line-plane intersection.
		# Since the plane normal is (0,0,1) and d=0, z is the only variable left.
		u = min.z / (min.z - max.z)
		return min + (max - min) * u

	def projection(self):
		self._ortho_projection = FBOWidget.projection(self)
		fov = 90.0
		near = 0.1
		far = 1000.0
		
		glPushMatrix()
		glLoadIdentity()
		gluPerspective(fov, self.size.ratio(), near, far)
		glScalef(1, -1.0, 1);
		p = glGetDouble(GL_MODELVIEW_MATRIX)
		glPopMatrix()
		return p
	
	def on_buttondown(self, pos, button):
		# transform position by camera
		world_pos = self.unproject(pos)

		if button == 1:
			self.on_select_start(pos)
		elif button == 3:
			self.on_pan_start(pos)
		elif button == 4:
			#if self._scale > 0.2:
			self.on_zoom(-1.1, pos)
		elif button == 5:
			self.on_zoom(1.1, pos)

	def on_buttonup(self, pos, button):
		if button == 1:
			self.on_select_stop(pos)
		elif button == 3:
			delta = self.on_pan_stop(pos)
			if delta.length_squared() < 5:
				print 'move'
	
	def on_mousemove(self, pos, buttons):
		world_pos = self.unproject(pos)

		if buttons[1] and self._is_selecting:
			self.on_select_move(pos)

		if buttons[3] and self._is_panning:
			self.on_pan_move(pos)

	#
	# Zooming
	#

	def on_zoom(self, amount, ref):
		a = self.unproject(ref)
		self._scale += amount
		self._calc_view_matrix()
		b = self.unproject(ref)

		delta = b-a
		self._camera.x -= delta.x
		self._camera.y -= delta.y
		self._camera.z = 50 + self._scale
		self._calc_view_matrix()

	#
	# Panning
	#

	def on_pan_start(self, pos):
		self._is_panning = True
		self._panstart_screen = pos.copy()
		self._panstart = self.unproject(pos)
		self._panref = self._camera.copy()
		self._panrefview = copy(self._view)
		self.focus_lock()

	def on_pan_stop(self, pos):
		self._is_panning = False
		self.focus_unlock()
		return pos - self._panstart_screen

	def on_pan_move(self, pos):
		rel = self.unproject(pos,self._panrefview) - self._panstart
		self._camera.x = self._panref.x - rel.x
		self._camera.y = self._panref.y - rel.y
		self._calc_view_matrix()

	#
	# Selection
	#
	
	def on_select_start(self, pos):
		self._is_selecting = True
		self._selection_ref_a = self.unproject(pos)
		self._selection_ref_b = self.unproject(pos)

	def on_select_stop(self, pos):
		if not self._is_selecting:
			return

		self._is_selecting = False

		a = self._selection_ref_a
		b = self._selection_ref_b
		a_min = Vector3(min(a.x,b.x), min(a.y,b.y), 0)
		a_max = Vector3(max(a.x,b.x), max(a.y,b.y), 0)

		multiselect = (a-b).length() > 0.1

		selection = []
		for e in self._entities.values():
			p = e.position

			# @todo @refactor AABB-AABB overlapping
			b_min = p - Vector3(0.5,0.5,0) * e.type.size
			b_max = p + Vector3(0.5,0.5,0) * e.type.size # @todo Hardcoded size @entsize

			if a_max.x <  b_min.x or a_min.x > b_max.x:
				continue
			if a_max.y <  b_min.y or a_min.y > b_max.y:
				continue

			selection.append(e)

		if not multiselect and len(selection)>1:
			selection = [selection[-1]]
		
		self.on_selection(selection)

	def on_select_move(self, pos):
		self._selection_ref_b = self.unproject(pos)

	#
	# Entity selected
	#
	
	def on_selection(self, selection):
		print 'selection:', selection

		for e in self._selection:
			e.__selected = False

		for e in selection:
			e.__selected = True

		self._selection = selection
		
		if len(selection) == 1:
			entity = selection[0]
			if self.parent.find_window(entity.id) is not None:
				return

			info = self._client.entity_info(entity.id)
			self._client.add_window(EntityWindow(entity, info))
			return

	def on_resize(self, size, final):
		FBOWidget.on_resize(self, size, final)
		#self._viewport[2] = size.x
		#self._viewport[3] = size.y
		
		# use the parent size (which is a composite)
		#FBOWidget.on_resize(self, self.parent.size, final)
		self._viewport[2] = int(self.parent.size.x)
		self._viewport[3] = int(self.parent.size.y)
		self._calc_view_matrix()
	
	#
	# Rendering
	#

	def visible(self, sorted=False):
		r = self._rect
		l = filter(lambda e: e.intersect_rect(r), self._entities.values())

		def c(e1,e2):
			if e1.type.name == "Planet":
				if e2.type.name == "Planet":
					return 0
				else:
					return -1
			else:
				return 0

		if sorted:
			l.sort(cmp=c)
		return l
	
	@staticmethod
	def draw_quad():
		glBegin(GL_QUADS)
		glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, 0)
		glTexCoord2f(0, 1);	glVertex3f(-0.5,  0.5, 0)
		glTexCoord2f(1, 1);	glVertex3f( 0.5,  0.5, 0)
		glTexCoord2f(1, 0);	glVertex3f( 0.5, -0.5, 0)
		glEnd()

	@staticmethod
	def draw_aabb():
		glBegin(GL_LINE_STRIP)
		glVertex3f(-0.5, -0.5, 0)
		glVertex3f(-0.5,  0.5, 0)
		glVertex3f( 0.5,  0.5, 0)
		glVertex3f( 0.5, -0.5, 0)
		glVertex3f(-0.5, -0.5, 0)
		glEnd()

	@classmethod
	def draw_entity_full(cls, e, p):
		""" Draw entity as a regular sprite """

		glBindTexture(GL_TEXTURE_2D, e.sprite)
		glScalef(e.type.size, e.type.size, 1.0)

		if p == 0:
			cls.draw_quad()	
		elif p == 1 and e.__selected:
			glDisable(GL_TEXTURE_2D)
			glColor4f(1,1,0,1)
			cls.draw_aabb()
			glColor4f(1,1,1,1)
			glEnable(GL_TEXTURE_2D)

	def draw_entity_marker(self, e, p):
		if p != 1: return
		
		global MIN_SIZE_THRESHOLD
		scale = MIN_SIZE_THRESHOLD * self._rect.w / self.size.x
		glScalef(scale, scale, 1.0)

		glDisable(GL_TEXTURE_2D)
		glColor4f(1,1,0,1)
		self.draw_aabb()
		glColor4f(1,1,1,1)
		glEnable(GL_TEXTURE_2D)
	
	def do_render(self):
		global MIN_SIZE_THRESHOLD
		
		glClearColor(0,0,0,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self._render_background()

		# load view matrix
		glLoadIdentity()
		glMultMatrixd(self._view)

		glPushAttrib(GL_ENABLE_BIT)
		glEnable(GL_DEPTH_TEST)
		e = self.visible(sorted=True)
		self._render_entities(e, p=0)
		self._render_entities(e, p=1)
		self._render_selection()
		glPopAttrib()
		
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
				self._camera.x * s,
				self._camera.y * s,
				1.0 + i * 0.4,
				1.0 + i * 0.6)
			glBegin(GL_QUADS)
			glTexCoord2f(t.x, 1-t.y)
			glVertex2f(0, 0)
			
			glTexCoord2f(t.x, 1-t.y + t.h)
			glVertex2f(0, self.height)
			
			glTexCoord2f(t.x + t.w, 1-t.y + t.h)
			glVertex2f(self.width, self.height)
			
			glTexCoord2f(t.x + t.w, 1-t.y)
			glVertex2f(self.width, 0)
			glEnd()
		
		
		glBindTexture(GL_TEXTURE_2D, 0)
		
		# restore matrices
		glPopMatrix()
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)

	def _render_entities(self, entities, p):
		""" Renders all visible entities using pass P.
		    Pass 0: Geometry
			Pass 1: Selections + markers
		"""
		glDisable(GL_CULL_FACE)

		glColor4f(1,1,1,1)
		for e in entities:
			# estimate the screenspace size to select rendering mode
			ex = e.type.size / self._rect.w * self.size.x
			ey = e.type.size / self._rect.h * self.size.y
			ep = min(ex, ey)
			
			glPushMatrix()
			glTranslate(e.position.x, e.position.y, e.position.z)

			# Select different rendering styles depending of the screenspace it
			# would occupy. It helps when the objects are very small.
			if ep > MIN_SIZE_THRESHOLD:
				self.draw_entity_full(e, p)
			else:
				self.draw_entity_marker(e, p)
			
			glPopMatrix()

	def _render_selection(self):
		if not self._is_selecting:
			return
		
		a = self._selection_ref_a
		b = self._selection_ref_b

		glDisable(GL_TEXTURE_2D)
		glColor4f(1,1,0,1)
		glBegin(GL_LINE_STRIP)
		glVertex3f(a.x, a.y, 0)
		glVertex3f(a.x, b.y, 0)
		glVertex3f(b.x, b.y, 0)
		glVertex3f(b.x, a.y, 0)
		glVertex3f(a.x, a.y, 0)
		glEnd()
		glColor4f(1,1,1,1)
		glEnable(GL_TEXTURE_2D)
