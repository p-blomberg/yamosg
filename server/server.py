import os.path, sys
from time import sleep, clock, time

# relative path to this script
scriptfile = sys.modules[__name__].__file__
scriptpath = os.path.dirname(scriptfile) or '.'
root = os.path.normpath(os.path.join(scriptpath, '..'))

# add rootdir to pythonpath
sys.path.append(root)

from serversocket import ServerSocket
import entity
import player
from common.vector import Vector
from common.command import Command
from common import command
import socket
import traceback

class Server(ServerSocket):
	def __init__(self, host, port, split="\n", debug=False):
		ServerSocket.__init__(self, host, port, 0, split, debug)
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

	def tick(self):
		self.game.tick()

	def main(self):
		t=clock()
		while True:
			self.tick()
			self.checkSockets()
			new_time=clock()
			st=(1.0/15)-(new_time-t)
			if(st>0):
				sleep(st)
			t=new_time

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
			"NEWUSER": self.game.NewUser,
			"LIST_OF_ENTITIES": self.game.list_of_entities,
			"ENTACTION": self.game.EntAction,
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
	entities=[]
	tick_counter=0

	def __init__(self, split):
		self.split=split
		# Create world
		p=entity.Planet(len(self.entities), Vector(1,2,3), 20, self)
		cargo={
			entity.CopperOre(p, None, self):600
		}
		p.cargo=cargo
		self.entities.append(p)
	
	def unicast(self, socket, command, *args):
		""" Send a message to a specific client """
		cmd = Command(command, *args, id='UNICAST')
		socket.send(socket, str(cmd) + self._split)
	
	def broadcast(self, command, *args):
		""" Send a message to all connected clients """
		cmd = Command(command, *args, id='BROADCAST')
		for c in self.clients.keys():
			try:
				c.send(str(cmd) + self.split)
			except socket.error:
				traceback.print_exc()
				del self.clients[c]

	def tick(self):
		self.tick_counter+=1
		key_tick=False
		if(self.tick_counter==15):
			key_tick=True
			self.tick_counter=0
		for p in self.players:
			p.tick(key_tick)
		for o in self.entities:
			o.tick(key_tick)

	def list_of_entities(self, useless, useless2):
		foo=""
		for ent in self.entities:
			foo=foo+str(ent)+self.split
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
		self.broadcast('NEW_PLAYER', id, name)
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
		self.broadcast('USER_LOGIN', id, name)
		return str(id)

	def EntAction(self, connection, params):
		try:
			ent_id=int(params[0])
		except ValueError:
			response="NOT_OK: Invalid ID"
			return response
		try:
			ent=self.entities[ent_id]
			player=connection.player
			if not ent in player.entities:
				return "NOT_OK: Belongs to other player"

			response=ent.action(params[1:])
			print response
		except KeyError:
			response="I don't know the entity '"+ent_id+"'"
		return response
