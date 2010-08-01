import entity
from common.vector import Vector

class Player:
	def __init__(self, id, name, game):
		self.id=id
		self.name = name
		self.cash = 100000
		self.entities = list()
		
		gateway = entity.Gateway(Vector(4,6,0), game, owner=self)
		
		self.entities.append(gateway)
		game.add_entity(gateway)

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
		return "Name:%s Cash:%i" % (self.name, self.cash)

	def tick(self, key_tick):
		pass
