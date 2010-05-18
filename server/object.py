class Object:
	id=None
	owner=None
	position=None
	game=None

	def __init__(self, id, owner, position, game):
		self.owner=owner
		self.position=position
		self.game=game

	def __str__(self):
		return str(self.__class__)+", id: "+str(self.id)+", position: "+str(self.position)+", owner: "+str(self.owner)

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
	
	def build(self, params):
		types = {
			"STATION": Station,
			"SHIP": Ship
		}
		try:
			id=len(self.game.objects)
			obj=types[params[0]](id, self.owner, self.position, self.game)
			self.game.objects.append(obj)
			self.owner.objects.append(obj)
		except KeyError:
			response="Cannot build object of type '"+params[0]+"' from Gateway"
		return response

	def action(self, params):
		action=params[0]
		actions = {
			"BUILD": self.build
		}
		try:
			response=actions[action.strip()](params[1:])
		except KeyError:
			response="OBJACTION '"+action+"' is not valid for Gateway"
		return response
