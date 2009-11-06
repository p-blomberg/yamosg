class Game:
	# Swap this for real login code later.
	logins={
		'topace':'god',
		'slafs':'barfoo'
	}
	clients={}
	players=[]
	objects=[]

	def list_of_objects(self, useless, useless2):
		foo=""
		for obj in self.objects:
			foo=foo+str(obj)
		return foo

	def NewUser(self, connection, params):
		try:
			name=params[0]
			password=params[1]
		except KeyError:
			return "NOT_OK: Invalid number of arguments"
		if name in self.logins:
			return "NOT_OK: User already exists"
		else:
			self.logins[name]=password
			return "OK"

	def NewPlayer(self, name):
		id=len(self.players)
		self.players.append(Player(id, name))
		# Might want to push info to all players here.
		return id

	def playerinfo(self, connection, params):
		print connection
		print params
		if len(params)!=1:
			return "NOT_OK"
		return self.players[int(params[1])].info()

	def login(self, connection, params):
		print params
		if len(params)!= 2:
			return "NOT_OK"
		(name, passwd) = (params[0], params[1])
		if not name in self.logins:
			return "NOT_OK"
		if not self.logins[name] == passwd:
			return "NOT_OK"
		# insert some code to take command of existing player if same login.
		id=self.NewPlayer(name)
		connection.player=self.players[id]
		return str(id)
	
	def build(self,player,params):
		object_type=params[0]
		object_types = {
			"Ship": Ship(0,(1,2)),
			"Station": Station(0,(3,4))
		}
		try:
			obj=object_types[object_type]
		except KeyError:
			response="I don't know how to build a "+object_type
			return response
		if(player.can_afford(obj.cost)):
			self.objects.append(obj) # Perhaps some way to connect the object to the player?
			player.buy(obj.cost)
			return "Ok"
		raise NotEnoughCashError("Not Enough Cash")

	def action(self, connection, params):
		player=connection.player
		subcommands = {
			"BUILD": self.build
		}
		try:
			response=subcommands[params[0].strip()](player,params[1:])
		except KeyError:
			response="I don't know the command ACTION '"+params[0]+"'"
		return response
