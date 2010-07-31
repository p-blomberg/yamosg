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

def smart_truncate(content, length=100, suffix='...'):
	# Based on implementation found at:
	# http://stackoverflow.com/questions/250357/smart-truncate-in-python
	if len(content) <= length:
		return content
	else:
		return content[:length].rsplit(' ', 1)[0] + suffix

class Server(ServerSocket):
	def __init__(self, host, port, split="\n", debug=False):
		ServerSocket.__init__(self, host, port, 0, split, debug)
		self.game=Game(split)
		self.sockets=self._socketlist.copy()
		
		# Server commands
		self._commands = {
			'CAPS': self._get_caps
		}
		
		print "ready"
		
	def readCall(self, clientsocket, lines):
		changed_sockets = self._socketlist - self.sockets
		self.sockets=self._socketlist.copy()
		for sock in changed_sockets:
			if self.game.clients.has_key(sock):
				del self.clients[sock]
			else:
				self.game.clients[sock]=Connection(sock, self.game)
		
		# Get client for this socket, or create new client if not previously
		# connected.
		try:
			client = self.game.clients[clientsocket]
		except KeyError:
			client = Connection(clientsocket)
			self.game.clients[clientsocket] = client
		
		# Call commands
		for line in lines:
			response = self._dispatch_command(client, line)
			print '{peer} {line} -> {response}'.format(
				peer=clientsocket.getpeername(),
				line=[line], 
				response=[smart_truncate(response, length=50)])
			self.write(clientsocket, [response + self._split])
	
	def _dispatch_command(self, client, line):
		"""
		Try to parse the line and dispatch the command to the relevant
		destination (server or client).
		"""
		
		# Try to parse the line
		try:
			counter, cmd, args = command.parse(line)
		except Exception, e:
			return '0 NOT_OK ' + str(e)
		
		# See if the server handles this command
		func = self._commands.get(cmd, None)
		
		# Dispatch
		if func is not None:
			response = func(*args)
		else:
			response = client.command(cmd, args)
		
		# Generate full response
		return '{id} {response}'.format(id=counter, response=response)

	def _get_caps(self):
		"""
		Get this servers extended capabilities
		"""
		return []
	
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
		
		# client commands
		self._commands = {
			"LOGIN": self.game.login,
			"PING": self.ping,
			"PLAYERINFO": self.game.playerinfo,
			"NEWUSER": self.game.NewUser,
			"LIST_OF_ENTITIES": self.game.list_of_entities,
			"ENTACTION": self.game.EntAction,
			"PLAYERS": self.game.Players
		}
	
	def ping(self, other, parts):
		print parts
		try:
			return "PONG "+parts[0]
		except IndexError:
			return "ERR_BAD_PARAMS"

	def command(self, cmd, args):
		func = self._commands.get(cmd, lambda *args: "I don't know the command " + cmd)
		
		try:
			return func(self, *args)
		except CommandError, e:
			return 'NOT_OK ' + str(e)
		except TypeError, e:
			traceback.print_exc()
			return 'NOT_OK ' + str(e)

class Game:
	def __init__(self, split):
		self.split=split
		self.logins={}
		self.clients={}
		self.players=[]
		self._entities={}
		self.tick_counter=0
	
		# Create world
		p=entity.Planet(Vector(30,30,0), 20, self)
		cargo={
			entity.CopperOre(container=p, owner=None, game=self): 600
		}
		p.cargo=cargo
		self.add_entity(p)
	
	def add_entity(self, ent):
		"""
		Add an entity to the game world
		"""
		
		if ent.id in self._entities:
			raise RuntimeError, 'duplicate entities with id ' + ent.id
		self._entities[ent.id] = ent
	
	def entity_by_id(self, id):
		"""
		Get an entity by its ID, return None if there is no such entity.
		"""
		return self._entities.get(id, None)
	
	def all_entities(self):
		"""
		Generator to get all entities in the world.
		"""
		for ent in self._entities.values():
			yield ent
	
	def entities_matching(self, *func, **criteria):
		"""
		Search for entities matching the specified criteria. Just like
		all_entities it is a Generator.
		
		Pass kwargs where the key is the entity variable you would like to
		match against the value.
		
		Eg:
		>>> entities_matching(minable=True)
		
		will examine the variable "minable" and would only match if the value
		is the same (True in this case).
		
		Pass variable arguments as functions to evaluate if the entity is
		matching. The function receives only single entity should return
		either True or False.
		
		Eg:
		>>> entities_matching(lambda x: (x.position - self.position).length() < 10.0)
		
		will call the lambda for each entity and only yields entities where it
		returns True.
		"""
		
		def match_criteria(e):
			for k,v1 in criteria.items():
				v2 = getattr(ent, k)
				
				if v1 != v2:
					return False
			
			return True
		
		def match_func(e):
			for f in func:
				if not f(ent):
					return False
			
			return True
		
		for ent in self._entities.values():
			if not match_criteria(e):
				continue
			
			if not match_func(e):
				continue
			
			yield ent
	
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
		for o in self._entities.values():
			o.tick(key_tick)

	def list_of_entities(self, connection):
		return "OK "+json.dumps([x.dinmamma() for x in self._entities.values()])

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
		ent = self.entity_by_id(id)
		if ent is None:
			raise CommandError, 'Invalid ID'
		
		player = connection.player
		if not ent in player.entities:
			raise CommandError, 'Belongs to other player'

		return ent.action(action, args)
