import entity
from common.vector import Vector
import hashlib

class Player:
	_counter = 0
	__salt = 'yamosg_salt_omg'
	
	def __init__(self, name, game, id=None, cash=100000):
		self.id = id or self._generate_id()
		self.name = name
		self.cash = cash
		self.entities = list()
		
		# Client connection or None if not logged in.
		self._client = None
		
		# Credentials
		self._password = None
		
		gateway = entity.Gateway(Vector(4,6,0), game, owner=self)
		
		self.entities.append(gateway)
		game.add_entity(gateway)
	
	def _generate_id(self):
		Player._counter += 1
		return Player._counter
	
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

	def __str__(self):
		return self.name

	def can_afford(self, amount):
		if(self.cash >= amount):
			return True
		return False

	def buy(self, amount):
		if self.can_afford(amount):
			self.cash -= amount
			return True
		return False

	def info(self):
		return {
			'name': self.name,
			'cash': self.cash
		}

	def tick(self, key_tick):
		pass
