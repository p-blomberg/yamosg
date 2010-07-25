from common.vector import Vector

class Entity:
	def __init__(self, Type, Id, Position, Cargo, Speed, Minable, Owner):
		self._type = Type
		self._id = Id
		self._position = Vector(*Position)
		self._cargo = Cargo
		self._speed = Vector(*Speed)
		self._minable = Minable
		self._owner = Owner

	def __str__(self):
		return '<Entity pos=%s>' % (str(self._position))
