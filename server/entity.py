from common.vector import Vector

class Entity:
	id=None
	owner=None
	position=None
	game=None
	max_speed=None
	size=None
	speed=None
	actions={}

	def __init__(self, id, owner, position, game):
		self.id=id
		self.owner=owner
		self.position=position
		self.game=game
		self.speed=Vector(0,0,0)

	def __str__(self):
		return str(self.__class__)+", id: "+str(self.id)+", position: "+str(self.position)+", owner: "+str(self.owner)+", speed: "+str(self.speed)

	def go(self, params):
		speed=Vector(params[0], params[1], params[2])
		if(speed.length() > self.max_speed):
			return "NOT_OK: Max speed for "+self.__class__.__name__+" is "+str(self.max_speed)
		self.speed=speed
		return "OK"

	def action(self, params):
		action=params[0]
		self.actions["GO"]=self.go
		try:
			response=self.actions[action.strip()](params[1:])
		except KeyError:
			response="NOT_OK: ENTACTION %s is not valid" %(action)
		return response

	def tick(self, key_tick):
		self.position=self.position+(self.speed*(1./15))

class Planet(Entity):
	pass

class Ship(Entity):
	max_speed = 1
	cost = 40000
	size = 0.1

class Station(Entity):
	cost = 250000
	size = 10

class Miner(Ship):
	max_speed=0.1
	size=0.2
	cost=50000
	
	def mine(self):
		pass

	def action(self, params):
		self.actions["MINE"]=self.mine
		parent.action(params)

class Gateway(Station):
	cost = 10000000
	size = 10
	
	def build(self, params):
		types = {
			"STATION": Station,
			"SHIP": Ship
		}
		try:
			id=len(self.game.entities)
			ent=types[params[0]](id, self.owner, self.position, self.game)
			if(self.owner.buy(ent.cost)):
				self.game.entities.append(ent)
				self.owner.entities.append(ent)
				return id
			return "NOT_OK: Not enough cash"
		except KeyError:
			return "Cannot build entity of type '"+params[0]+"' from Gateway"

	def action(self, params):
		action=params[0]
		actions = {
			"BUILD": self.build
		}
		try:
			response=actions[action.strip()](params[1:])
		except KeyError:
			response="ENTACTION %s is not valid for Gateway" %(action)
		return response
