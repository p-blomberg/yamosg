from common.vector import Vector
from copy import copy
import json

class Entity:
	id=None
	owner=None
	container=None
	position=None
	game=None
	max_speed=None
	size=None
	mass=None
	speed=None
	actions={}
	minable=False
	max_cargo=0

	def __init__(self, id, owner, position, game):
		self.id=id
		self.owner=owner
		self.position=position
		self.game=game
		self.speed=Vector(0,0,0)
		self.cargo = {}
		self.actions["GO"]=self.go

	def __str__(self):
		return self.encode()
		return str(self.__class__)+", id: "+str(self.id)+", position: "+str(self.position)+", owner: "+str(self.owner)+", speed: "+str(self.speed)+", cargo: "+str(self.cargo);

	def dinmamma(self):
		d={
			"Type" : self.__class__.__name__,
			"Id": self.id,
			"Owner": str(self.owner.id),
			"Position": str(self.position),
			"Speed": str(self.speed),
			"Minable": self.minable,
			"Cargo": [(cargo.dinmamma(), amount) for cargo,amount in self.cargo.items()]
		}
		return d

	def encode(self):
		return json.dumps(self.dinmamma())

	def remaining_cargo_space(self):
		return self.max_cargo - self.cargo_sum()

	def cargo_sum(self):
		return reduce(lambda sum, x: sum+x, self.cargo.values(), 0)

	def retrieve_cargo(self, cargo, amount):
		""" Attempt to transfer the specified cargo from its container to this entity.
				If the specified amount is not available in the container,
				the maximum available amount will be transferred.
				If the cargo cannot fit in this entity, the maximum amount
				will be transferred.
				@return int amount of fetched cargo.
		"""

		entity=cargo.container

		# Calculate amount
		if(entity.cargo[cargo] >= amount):
			if(amount <= self.remaining_cargo_space()):
				actual_amount=amount
			else:
				actual_amount=self.remaining_cargo_space()
		else:
			if(amount <= self.remaining_cargo_space()):
				actual_amount=entity.cargo[cargo]
			else:
				actual_amount=self.remaining_cargo_space()

		# Do the transfer
		entity.cargo[cargo]-=actual_amount
		if(cargo in self.cargo):
			self.cargo[cargo]+=actual_amount
			print "Adding "+str(actual_amount)+" of "+cargo.__class__.__name__+" to "+str(self.id)
		else:
			#print cargo.hash()+" is not "+self.cargo[0].hash()
			print str(self.id)+" now also contains "+cargo.__class__.__name__
			c=copy(cargo)
			self.cargo[c]=actual_amount

		# Check if remaining amount is zero - delete useless entity
		if(entity.cargo[cargo]==0):
			del entity.cargo[cargo]
			
		return actual_amount

	def go(self, params):
		print params
		speed=Vector(params[0], params[1], params[2])
		if(speed.length() > self.max_speed):
			return "NOT_OK: Max speed for "+self.__class__.__name__+" is "+str(self.max_speed)
		self.speed=speed
		return "OK"

	def action(self, action, args):
		try:
			response=self.actions[action](*args)
		except KeyError:
			response="NOT_OK: ENTACTION %s is not valid" %(action)
		return response

	def tick(self, key_tick):
		self.position=self.position+(self.speed*(1./15))

class Planet(Entity):
	minable=True

	def __init__(self, id, position, size, game):
		Entity.__init__(self, id, None, position, game)
		self.size=size
		self.mass=2000*size

class Ship(Entity):
	max_speed = 1
	cost = 40000
	size = 0.1
	mass = 300

class Station(Entity):
	cost = 250000
	size = 10
	mass = 5000

class Mineral(Entity):
	size = 0.001
	mass = 1

	def __hash__(self):
		h="".join([str(ord(i)) for i in self.__class__.__name__])
		return int(h)

	def __cmp__(self, other):
		if (self.__hash__()==other.__hash__()):
			return 0
		else:
			return 1

	def __init__(self, container, owner, game):
		id=None
		position=None
		self.container=container
		Entity.__init__(self, id, owner, position, game)

class CopperOre(Mineral):
	pass

class Miner(Ship):
	max_speed=0.1
	size=0.2
	cost=50000
	mining_speed=1.0
	max_cargo = 50
	cargo_type=None

	def __init__(self, id, owner, position, game):
		Ship.__init__(self, id, owner, position, game)
		self.actions['GO_TO_PLANET']=self.go_to_planet
		self.actions['SET_CARGO_TYPE']=self.set_cargo_type

	def set_cargo_type(self, type):
		self.cargo_type=type[0]
		return "OK"

	def go_to_planet(self):
		self.position=Vector(30, 9.6, 0)
		return "OK"
	
	def go_to_gateway(self):
		self.position=Vector(4, 6, 0)
		return "OK"

	def mine(self, entity):
		for c in entity.cargo:
			if(c.__class__.__name__ == self.cargo_type):
				print "Mining "+self.cargo_type
				self.retrieve_cargo(c, self.mining_speed)
			else:
				print "Not mining - wrong cargo type. Avail cargo: "+c.__class__.__name__+", requested: "+str(self.cargo_type)

	def tick(self, key_tick):
		Entity.tick(self, key_tick)
		if(key_tick):
			if(self.cargo_sum() < self.max_cargo):
				# Look for nearby minable entities
				for e in self.game.entities:
					if(e.minable):
						distance=(e.position-self.position).length()
						if(distance - e.size - self.size < 0.5):
							self.mine(e)

class Gateway(Station):
	cost = 10000000
	size = 10
	
	def build(self, type):
		print type
		types = {
			"STATION": Station,
			"SHIP": Ship,
			"MINER": Miner
		}
		try:
			id=len(self.game.entities)
			ent=types[type](id, self.owner, self.position, self.game)
			if(self.owner.buy(ent.cost)):
				self.game.entities.append(ent)
				self.owner.entities.append(ent)
				return "OK: ID="+str(id)
			return "NOT_OK: Not enough cash"
		except KeyError:
			return "Cannot build entity of type '"+type+"' from Gateway"

	def load(self, ship_id):
		entity=self.game.entities[int(ship_id)]
		print entity
		return "OK"

	def __init__(self, id, owner, position, game):
		Station.__init__(self, id, owner, position, game)
		self.actions['BUILD']=self.build
		self.actions['LOAD']=self.load

