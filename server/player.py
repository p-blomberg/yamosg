class Player:
	name=''
	id=None
	cash=0
	def __init__(self, id, name):
		self.id=id
		self.name = name
		self.cash = 1000
		self.objects = list()

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

