#!/usr/bin/python
# -*- coding: utf-8 -*-

import entity
from common.vector import Vector3
import hashlib
import sqlite3

class Player:
	_counter = 0
	__salt = 'yamosg_salt_omg'
	
	def __init__(self, username, game, id=None, password=None, cash=1000000):
		self.id = id
		self.name = username
		self.game = game
		self.cash = cash
		self.entities = list()
		
		# Client connection or None if not logged in.
		self._client = None
		
		# Credentials
		self._password = password
		
		gateway = entity.Gateway(Vector3(4,6,0), game, owner=self)
		
		self.entities.append(gateway)
		game.add_entity(gateway)
	
	def set_id(self, id):
		self.id = id
	
	def serialize(self):
		return {
			'id': self.id,
			'username': self.name,
			'password': self._password,
			'cash': self.cash
		}
	
	def _hash(self, line):
		"""
		Returns the hash of line with salt prepended.
		"""
		
		h = hashlib.sha256()
		h.update(Player.__salt)
		h.update(line)
		return h.digest()
	
	def check_password(self, password):
		"""
		Check if the supplied password matches the stored
		"""
		
		return self._password == self._hash(password)
		
	def set_password(self, password, old_password=None):
		"""
		Sets or changes the password. If old_password is provided it is
		compared against the current password and only updates if they match.
		
		(the only way a user is supposed to "call" this is using their old
		password, or else it is a flaw of the public interface)
		
		Returns whenever it succeded or not.
		"""
		
		# match old password
		if old_password and not check_password(old_password):
			return False
		
		# update
		self._password = self._hash(password)
		return True
	
	def login(self, client, password):
		"""
		Try to login using the supplied credentials. If the player is already
		logged in the other session will be disconnected.
		"""
		
		# check password
		if not self.check_password(password):
			return False
		
		# disconnect current session
		if self._client is not None:
			self._client.disconnect(message='Old session disconnected')
		
		self._client = client
		return True
	
	def logout(self, disconnected=False):
		"""
		Logout a player.
		@param disconnected If the server forces the logout due to a disconnect.: 
		"""
		
		if self._client is None:
			raise RuntimeError, 'Invalid player state for logout'
		
		if disconnected == False:
			self._client.disconnect('Logged out')
		
		self._client = None
	
	def is_online(self):
		return self._client is not None
	
	def __str__(self):
		return self.name

	def can_afford(self, amount):
		return self.cash >= amount

	def buy(self, amount):
		if self.can_afford(amount):
			self.cash -= amount
			
			# Tell player how much cash he have left
			self.game.unicast(self._client, 'CASH', self.cash)

			return True
		return False

	def sell(self, amount):
		self.cash += amount
		return True

	def info(self):
		return {
			'name': self.name,
			'cash': self.cash
		}

	def tick(self, key_tick):
		pass

	def persist(self):
		self.game._c.execute("""
			UPDATE players SET cash = :cash
		""", {"cash": self.cash})
		self.game._db.commit()

def create(name, password, game):
	player = Player(name, game)
	player.set_password(password)

	d = player.serialize()
	d['password'] = sqlite3.Binary(d['password'])
	game._c.execute("""
		INSERT INTO players (
			username, password, cash
		) VALUES (
			:username, :password, :cash
		)
	""", d)
	player.set_id(game._c.lastrowid)
	game._db.commit()

	return player
