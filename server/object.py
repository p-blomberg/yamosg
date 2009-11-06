class Object:
	owner_id=None
	position=None

	def __init__(self, owner_id, position):
		self.owner_id=owner_id
		self.position=position

	def __str__(self):
		return str(self.__class__)+", position: "+str(self.position)+", owner: "+str(self.owner_id)

class Planet(Object):
	max_speed = 0

class Ship(Object):
	max_speed = 10
	cost = 150

class Station(Object):
	max_speed = 0
	cost = 800

class Gateway(Station):
	cost = 1500
