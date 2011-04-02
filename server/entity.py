from common.vector import Vector3
from copy import copy
import json

class Entity:
	max_speed=None
	size=None
	mass=None
	minable=False
	max_cargo=0
	buildlist={}
	
	# used to autogenerate id
	_id_counter = 0

	def __init__(self, position, game, id=None, container=None, owner=None):
		self.id = id or self._generate_id()
		
		self.container=container
		self.owner=owner
		self.game=game
		
		self.position = position # where it currently is
		self._velocity = Vector3(0,0,0) # current (calculated) velocity
		self._dst = position # where it is going
		
		self.cargo = {}
		self.actions = {
			'MOVE': self.move
		}

	@classmethod
	def _generate_id(cls, tag=None):
		"""
		Generates and incremental ID based on the calling class' counter.
		If no tag is specified the classname is used, but beware that using the
		same tag in different classes *may* yield the same ID, so it is better
		to use the classname which already is unique among the classes.
		"""
		cls._id_counter += 1
		return '{tag}_{id:04}'.format(tag=tag or cls.__name__, id=cls._id_counter)
	
	def __str__(self):
		return self.encode()
		return str(self.__class__)+", id: "+str(self.id)+", position: "+str(self.position)+", owner: "+str(self.owner)+", velocity: "+str(self._velocity)+", cargo: "+str(self.cargo);

	def dinmamma(self):
		d={
			"Type" : self.__class__.__name__,
			"Id": self.id,
			"Owner": self.owner and self.owner.id or None,
			"Position": self.position and self.position.xyz() or None,
			"velocity": self._velocity.xyz(),
			"Minable": self.minable,
			"Cargo": [(cargo.dinmamma(), amount) for cargo,amount in self.cargo.items()],
			"Buildlist":self.buildlist.keys()
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

	def move(self, x, y, z):
		self._dst = Vector3(x, y, z)
		return "OK"

	def action(self, action, args):
		try:
			response=self.actions[action](*args)
		except KeyError:
			response="NOT_OK: ENTACTION %s is not valid" %(action)
		return response
	
	def _distance(self):
		""" Distance to destination """
		return (self.position - self._dst).length()
	
	def tick(self, key_tick):
		dt = 1./15
		
		# only move if we are to far from the target position
		if self._distance() > 1.0: # @todo use radius (or something better)
			# calculate new velocity
			f = 5000.0 # force
			a = f / self.mass # acceleration
			dir = (self._dst - self.position).normalize() # direction
			self._velocity += dir * a
			
			# clamp at max speed
			if self._velocity.length() > self.max_speed:
				self._velocity = self._velocity.normalize() * self.max_speed
		
			self.position += self._velocity * dt

class Planet(Entity):
	minable=True

	def __init__(self, position, size, game, **kwargs):
		Entity.__init__(self, position, game, **kwargs)
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
	
	def __init__(self, container, owner, game, **kwargs):
		Entity.__init__(self, position=None, game=game, container=container, owner=owner, **kwargs)

	def __hash__(self):
		h="".join([str(ord(i)) for i in self.__class__.__name__])
		return int(h)

	def __cmp__(self, other):
		if (self.__hash__()==other.__hash__()):
			return 0
		else:
			return 1



class CopperOre(Mineral):
	pass

class Miner(Ship):
	max_speed=0.1
	size=0.2
	cost=50000
	mining_speed=1.0
	max_cargo = 50
	cargo_type=None

	def __init__(self, *args, **kwargs):
		Ship.__init__(self, *args, **kwargs)
		self.actions['GO_TO_PLANET']=self.go_to_planet
		self.actions['SET_CARGO_TYPE']=self.set_cargo_type

	def set_cargo_type(self, type):
		self.cargo_type=type[0]
		return "OK"

	def go_to_planet(self):
		self.position=Vector3(30, 9.6, 0)
		return "OK"
	
	def go_to_gateway(self):
		self.position=Vector3(4, 6, 0)
		return "OK"

	def mine(self, entity):
		for c in entity.cargo:
			if(c.__class__.__name__ == self.cargo_type):
				print "Mining "+self.cargo_type
				self.retrieve_cargo(c, self.mining_speed)
			else:
				print "Not mining - wrong cargo type. Avail cargo: "+c.__class__.__name__+", requested: "+str(self.cargo_type)

	def _minable_entities(self, distance=0.5):
		def distance(e):
			distance=(e.position-self.position).length()
			return distance - e.size - self.size < distance
		
		return self.game.entities_matching(distance, minable=True)
	
	def tick(self, key_tick):
		Entity.tick(self, key_tick)
		if(key_tick):
			if(self.cargo_sum() < self.max_cargo):
				# Look for nearby minable entities
				for e in self._minable_entities():
					self.mine(e)

class Gateway(Station):
	max_speed = 0.2
	cost = 10000000
	size = 10
	buildlist = {
		"Station": Station,
		"Ship": Ship,
		"Miner": Miner
	}
	
	def build(self, type):
		# Get factory
		unit_type = self.buildlist.get(type, None)
		
		# See if we are able to build the specified unit
		if unit_type is None:
			return "NOT_OK: Cannot build entity of type '" + type + "' from Gateway"
		
		# Test if we can afford it
		if not self.owner.buy(unit_type.cost):
			return "NOT_OK: Not enough cash"
		
		# Build it
		ent = unit_type(self.position, self.game, owner=self.owner)

		# Add unit to world
		self.game.add_entity(ent)
		self.owner.entities.append(ent)
		
		# Successful unit is successful
		return "OK: ID="+str(ent.id)

	def load(self, ship_id):
		entity = self.game.entity_by_id(ship_id)
		
		for c in entity.cargo:
			self.retrieve_cargo(c, entity.cargo[c])
		
		return "OK"

	def __init__(self, *args, **kwargs):
		Station.__init__(self, *args, **kwargs)
		self.actions['BUILD']=self.build
		self.actions['LOAD']=self.load

