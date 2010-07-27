import entity
from common.vector import Vector

class Player:
	name=''
	id=None
	cash=0
	def __init__(self, id, name, game):
		self.id=id
		self.name = name
		self.cash = 100000
		self.entities = list()
		id=len(game.entities)
		self.entities.append(entity.Gateway(id, self, Vector(4,6,0), game))
		game.entities.append(self.entities[0])

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
