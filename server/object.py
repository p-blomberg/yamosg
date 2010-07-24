from common.vector import Vector

class Object:
	id=None
	owner=None
	position=None
	game=None
	max_speed=None
	size=None
	speed=None

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
		print action
		actions = {
			"GO": self.go
		}
		try:
			response=actions[action.strip()](params[1:])
		except KeyError:
			response="NOT_OK: OBJACTION %s is not valid" %(action)
		return response

class Planet(Object):
	pass

class Ship(Object):
	max_speed = 1
	cost = 40000
	size = 0.1

class Station(Object):
	cost = 250000
	size = 10

class Gateway(Station):
	cost = 10000000
	size = 10
	
	def build(self, params):
		types = {
			"STATION": Station,
			"SHIP": Ship
		}
		try:
			id=len(self.game.objects)
			obj=types[params[0]](id, self.owner, self.position, self.game)
			if(self.owner.buy(obj.cost)):
				self.game.objects.append(obj)
				self.owner.objects.append(obj)
				return id
			return "NOT_OK: Not enough cash"
		except KeyError:
			return "Cannot build object of type '"+params[0]+"' from Gateway"

	def action(self, params):
		action=params[0]
		actions = {
			"BUILD": self.build
		}
		try:
			response=actions[action.strip()](params[1:])
		except KeyError:
			response="OBJACTION %s is not valid for Gateway" %(action)
		return response
