from serversocket import ServerSocket
import object
import player

class Server(ServerSocket):
	def __init__(self, host, port, timeout=30, split="\n", debug=False):
		ServerSocket.__init__(self, host, port, timeout, split, debug)

		self.game=Game()
		self.sockets=self._socketlist.copy()
		
	def readCall(self, clientsocket, lines):
		changed_sockets = self._socketlist - self.sockets
		self.sockets=self._socketlist.copy()
		for sock in changed_sockets:
			if self.game.clients.has_key(sock):
				del self.clients[sock]
			else:
				self.game.clients[sock]=Connection(sock, self.game)
				self.write(sock,"Hello"+self._split)
			
		print clientsocket, lines
		for line in lines:
			try:
				response=self.game.clients[clientsocket].command(line)+self._split
			except KeyError:
				self.game.clients[clientsocket]=Connection(clientsocket)
				response=self.game.clients[clientsocket].command(line)+self._split
			self.write(clientsocket,[response])

class Connection:
	player=None
	def __init__(self, socket, game):
		self.socket=socket
		self.game=game
	
	def ping(self, other, parts):
		print parts
		try:
			return "PONG "+parts[0]
		except IndexError:
			return "ERR_BAD_PARAMS"

	def command(self, line):
		parts=line.split(' ')
		command=parts[0]
		commands = {
			"LOGIN": self.game.login,
			"PING": self.ping,
			"PLAYERINFO": self.game.playerinfo,
			"ACTION": self.game.action,
			"NEWUSER": self.game.NewUser,
			"LIST_OF_OBJECTS": self.game.list_of_objects
		}
		del parts[0]
		try:
			response=commands[command](self, parts)
		except KeyError:
			response="I don't know the command "+command
		return response


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
		self.players.append(player.Player(id, name, self))
		# Might want to push info to all players here.
		return id

	def playerinfo(self, connection, params):
		print connection
		print params
		if len(params)!=1:
			return "NOT_OK"
		return self.players[int(params[0])].info()

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
			"Ship": object.Ship(0,(1,2)),
			"Station": object.Station(0,(3,4))
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
