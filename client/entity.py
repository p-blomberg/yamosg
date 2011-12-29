from common.vector import Vector3
from OpenGL.GL import *
import pygame
import common.resources as resources

import os.path

_resources = {}

def load_sprite(filename):
	if filename in _resources:
		return _resources[filename]

	texture = glGenTextures(1)
	
	fp = resources.open(('textures',filename), 'rb')
	surface = pygame.image.load(fp).convert_alpha()
	data = pygame.image.tostring(surface, "RGBA", 0)

	glBindTexture(GL_TEXTURE_2D, texture)
	glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glBindTexture(GL_TEXTURE_2D, 0)

	_resources[filename] = texture
	return texture

class Entity:
	def __init__(self, Type, Id, Position, Cargo, Velocity, Minable, Owner, **kwargs):
		self._type = Type
		self.id = Id
		self.position = Vector3(*Position)
		self._cargo = Cargo
		self._velocity = Velocity and Vector3(*Velocity) or None
		self._minable = Minable
		self.owner = client.player_by_id(Owner)
		self.sprite = 0

		if Type == 'Planet':
			self.sprite = load_sprite('jupiter.png')
		elif Type == 'Gateway':
			self.sprite = load_sprite('gateway.png')

	def __str__(self):
		return '<Entity pos=%s>' % (str(self.position))

	def on_go(self, pos, button):
		print 'go', pos, button

	def update(self, info):
		if 'Position' in info:
			self.position = Vector3(*info['Position'])
