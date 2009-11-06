class Object:
	owner_id=None
	position=None

	def __init__(self, owner_id, position):
		self.owner_id=owner_id
		self.position=position

	def __str__(self):
		return str(self.__class__)+", position: "+str(self.position)+", owner: "+str(self.owner_id)

