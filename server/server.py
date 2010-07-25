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
import json

class CommandError (Exception):
	pass

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
	def __init__(self, socket, game):
		self.socket=socket
		self.game=game
		self.player=None
	
	def ping(self, other, parts):
		print parts
		try:
			return "PONG "+parts[0]
		except IndexError:
			return "ERR_BAD_PARAMS"

	def command(self, line):
		counter, cmd, args = command.parse(line)
		commands = {
			"LOGIN": self.game.login,
			"PING": self.ping,
			"PLAYERINFO": self.game.playerinfo,
			"NEWUSER": self.game.NewUser,
			"LIST_OF_ENTITIES": self.game.list_of_entities,
			"ENTACTION": self.game.EntAction,
			"PLAYERS": self.game.Players
		}
		
		func = commands.get(cmd, lambda *args: "I don't know the command " + cmd)
		try:
			reply = func(self, *args)
		except CommandError, e:
			reply = 'NOT_OK ' + str(e)
		except TypeError, e:
			traceback.print_exc()
			reply = 'NOT_OK ' + str(e)
		return '{id} {reply}'.format(id=counter, reply=reply)

class Game:
	logins={}
	clients={}
	players=[]
	entities=[]
	tick_counter=0

	def __init__(self, split):
		self.split=split
		# Create world
		p=entity.Planet(len(self.entities), Vector(30,30,0), 20, self)
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

	def list_of_entities(self, connection):
		return "OK "+json.dumps([x.dinmamma() for x in self.entities])

	def NewUser(self, connection, name, password):
		if name in self.logins:
			raise CommandError, 'Username already exists'
		else:
			self.logins[name]=password
			return "OK"

	def NewPlayer(self, name):
		id=len(self.players)
		self.players.append(player.Player(id, name, self))
		# push info to all players.
		self.broadcast('NEW_PLAYER', id, name)
		return id

	def playerinfo(self, connection, id):
		try:
			id = int(id)
		except ValueError:
			raise CommandError, 'Invalid ID'
		
		try:
			return self.players[id].info()
		except IndexError:
			raise CommandError, 'Invalid ID'

	def Players(self, connection):
		playerlist=str()
		for player in self.players:
			playerlist+=str(player.id)+":"+player.name+self.split
		return playerlist

	def login(self, connection, name, passwd):
		if not name in self.logins:
			raise CommandError, 'Invalid username or password'
		if not self.logins[name] == passwd:
			raise CommandError, 'Invalid username or password'
		
		# insert some code to take command of existing player if same login.
		id=self.NewPlayer(name)
		connection.player=self.players[id]
		# Send info to all players
		self.broadcast('USER_LOGIN', id, name)
		return "OK ID="+str(id)

	def EntAction(self, connection, id, action, *args):
		try:
			id = int(id)
		except ValueError:
			raise CommandError, 'Invalid ID'
		
		try:
			ent = self.entities[id]
		except KeyError:
			raise CommandError, 'Invalid ID'
		
		player = connection.player
		if not ent in player.entities:
			raise CommandError, 'Belongs to other player'

		response = ent.action(action, args)
		print response
		return response

