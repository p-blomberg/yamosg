import os.path, sys

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

# add rootdir to pythonpath
sys.path.append(root)

from serversocket import ServerSocket
import object
import player
from common import command

class Server(ServerSocket):
	def __init__(self, host, port, timeout=1, split="\n", debug=False):
		ServerSocket.__init__(self, host, port, timeout, split, debug)
		self.game=Game(split)
		self.sockets=self._socketlist.copy()
		print "ready"
		
	def readCall(self, clientsocket, lines):
		changed_sockets = self._socketlist - self.sockets
		self.sockets=self._socketlist.copy()
		for sock in changed_sockets:
			if self.game.clients.has_key(sock):
				del self.clients[sock]
			else:
				self.game.clients[sock]=Connection(sock, self.game)
			
		print clientsocket, lines
		for line in lines:
			try:
				response=str(self.game.clients[clientsocket].command(line))+self._split
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
		counter, cmd, parts = command.parse(line)
		commands = {
			"LOGIN": self.game.login,
			"PING": self.ping,
			"PLAYERINFO": self.game.playerinfo,
			"ACTION": self.game.action,
			"NEWUSER": self.game.NewUser,
			"LIST_OF_OBJECTS": self.game.list_of_objects,
			"OBJACTION": self.game.ObjAction,
			"PLAYERS": self.game.Players
		}
		try:
			response=str(commands[cmd](self, parts))
		except KeyError:
			response="I don't know the command "+cmd
		return str(counter)+' '+response

class Game:
	logins={}
	clients={}
	players=[]
	objects=[]
	def __init__(self, split):
		self.split=split

	def list_of_objects(self, useless, useless2):
		foo=""
		for obj in self.objects:
			foo=foo+str(obj)+self.split
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
		# push info to all players.
		for c in self.clients:
			c.send("BROADCAST NEW_PLAYER "+str(id)+" "+name+"\n")
		return id

	def playerinfo(self, connection, params):
		print connection
		print params
		if len(params)!=1:
			return "NOT_OK"
		
		id = int(params[0])
		
		try:
			return self.players[id].info()
		except IndexError:
			return "NOT_OK"

	def Players(self, connection, selection):
		playerlist=str()
		for player in self.players:
			playerlist+=str(player.id)+":"+player.name+self.split
		return playerlist

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
		# Send info to all players
		for c in self.clients:
			c.send("BROADCAST USER_LOGIN "+str(id)+" "+name+"\n")
		return str(id)

	def ObjAction(self, connection, params):
		try:
			obj_id=int(params[0])
		except ValueError:
			response="NOT_OK: Invalid ID"
			return response
		try:
			obj=self.objects[obj_id]
			player=connection.player
			if not obj in player.objects:
				return "NOT_OK: Belongs to other player"

			response=obj.action(params[1:])
			print response
		except KeyError:
			response="I don't know the object '"+obj_id+"'"
		return response
