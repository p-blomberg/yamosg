from common.vector import Vector3
from OpenGL.GL import *
import pygame
import common.resources as resources

import os.path
import rpc

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

class TypeInfo:
	lut = {}

	def __init__(self, name):
		TypeInfo.lut[name] = self
		self.name = name
		self.update()
	
	@staticmethod
	def by_name(name):
		try:
			return TypeInfo.lut[name]
		except KeyError:
			return TypeInfo(name)

	def update(self):
		info = rpc.typeinfo(self.name)
		self.max_cargo = info['max_cargo']
		self.max_speed = info['max_speed']
		self.max_minable = info['minable']
		self.size = info['size']

class Entity:
	def __init__(self, Type, Id, Position, Cargo, Velocity, Minable, Owner, **kwargs):
		self.type = TypeInfo.by_name(Type)
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
		elif Type == 'Miner':
			self.sprite = load_sprite('prospector.png')
		elif Type == 'Silo':
			self.sprite = load_sprite('silo.png')

	def __str__(self):
		return '<Entity pos=%s>' % (str(self.position))

	def on_go(self, pos, button):
		print 'go', pos, button

	def update(self, info):
		if 'Position' in info:
			self.position = Vector3(*info['Position'])

	def intersect_point(self, p):
		if p.x < self.position.x - 0.5 * self.type.size: return False
		if p.x > self.position.x + 0.5 * self.type.size: return False
		if p.y < self.position.y - 0.5 * self.type.size: return False
		if p.y > self.position.y + 0.5 * self.type.size: return False
		return True

	def intersect_rect(self, r):
		if r.x     > self.position.x + 0.5 * self.type.size: return False
		if r.x+r.w < self.position.x - 0.5 * self.type.size: return False
		if r.y     > self.position.y + 0.5 * self.type.size: return False
		if r.y+r.h < self.position.y - 0.5 * self.type.size: return False
		return True

	def __repr__(self):
		return '<Entity type=\"%s\" pos=\"%.2f %.2f %.2f\">' % ((self.type.name,) + self.position.xyz())

