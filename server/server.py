#!/usr/bin/python
# -*- coding: utf-8 -*-

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
from common.transcoder import encoder, encoders
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
		return {'ENCODERS': encoders()}
	
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
		self._encoder = encoder('plaintext')
		
		# client commands
		self._commands = {
			'SET': self._set_prop,
			"LOGIN": self.game.login,
			"PING": self.ping,
			"PLAYERINFO": self.game.playerinfo,
			"NEWUSER": self.game.NewUser,
			"LIST_OF_ENTITIES": self.game.list_of_entities,
			"ENTACTION": self.game.EntAction,
			"PLAYERS": self.game.Players
		}
		
		# properties
		self._props = {
			'ENCODER': self._set_encoder
		}
	
	def disconnect(self, message='Disconnected'):
		"""
		Force a client to disconnect.
		"""
		
		self.game.unicast(self.socket, 'DISCONNECTED', message)
		self.socket.shutdown(socket.SHUT_RDWR)
	
	def _set_prop(self, connection, key, value):
		if key not in self._props:
			raise CommandError, 'Invalid property'
		
		self._props[key](value)
	
	def _set_encoder(self, name):
		try:
			self._encoder = encoder(name)
		except KeyError:
			raise CommandError, 'Invalid value'
	
	def ping(self, other, parts):
		print parts
		try:
			return "PONG "+parts[0]
		except IndexError:
			return "ERR_BAD_PARAMS"

	def command(self, cmd, args):
		func = self._commands.get(cmd, lambda *args: "I don't know the command " + cmd)
		
		try:
			response = func(self, *args)
			
			# encode objects which aren't strings
			if not isinstance(response, basestring):
				# skip None
				if response is None:
					response = 'OK'
				else:
					response = 'OK ' + self._encoder.encode(response)
			
			return response
		except CommandError, e:
			# command contained an error which was handled by server and
			# contains a message to info the user about it.
			return 'NOT_OK "%s"' % str(e)
		except TypeError, e:
			# command didn't pass enought parameters.
			traceback.print_exc()
			return 'NOT_OK "%s"' % str(e)
		except:
			# an unhandled exception occured. Will not pass an specific details
			# to the client. 
			traceback.print_exc()
			return 'NOT_OK "An unexpected error occured. Try again later."'

class Game:
	def __init__(self, split):
		self._split=split
		self.clients={}
		self._players={}  # all players in the world. 
		self._entities={} # all entities in the world.
		self.tick_counter=0
		
		# temporary player storage @tempstore
		import sqlite3
		self._db = sqlite3.connect('players.db')
		self._db.row_factory = sqlite3.Row
		self._c = self._db.cursor()
		self._c.execute('PRAGMA foreign_keys = ON')
		self._c.execute("""
			CREATE TABLE IF NOT EXISTS players (
				id INTEGER UNIQUE NOT NULL,
				username TEXT PRIMARY KEY,
				password BLOB NOT NULL,
				cash INTEGER NOT NULL
			)""")
		for row in self._c.execute('SELECT id, username, password, cash FROM players').fetchall():
			d = dict(**row)
			d['password'] = str(d['password'])
			self.add_player(player.Player(game=self, **d))
		
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
		
		def match_criteria(ent):
			for k,v1 in criteria.items():
				v2 = getattr(ent, k)
				
				if v1 != v2:
					return False
			
			return True
		
		def match_func(ent):
			for f in func:
				if not f(ent):
					return False
			
			return True
		
		for ent in self._entities.values():
			if not match_criteria(ent):
				continue
			
			if not match_func(ent):
				continue
			
			yield ent
	
	def add_player(self, player):
		self._players[player.name] = player
		self.player_persist()
	
	def player_persist(self):
		import sqlite3
		
		# temporary player storage @tempstore
		self._c.execute('DELETE from players')
		self._db.commit()
		for player in self._players.values():
			d = player.serialize()
			d['password'] = sqlite3.Binary(d['password'])
			
			self._c.execute("""
				INSERT INTO players (
					id, username, password, cash
				) VALUES (
					:id, :username, :password, :cash
				)
			""", d)
		self._db.commit()
	
	def player_by_id(self, id):
		"""
		Get player by its ID. It is an O(n) operation, prefer player_by_username
		"""
		
		for p in self._players.values():
			if p.id == id:
				return p
		return None
	
	def player_by_username(self, username):
		"""
		Get player by username
		"""
		
		return self._players.get(username, None)
	
	def unicast(self, socket, command, *args):
		""" Send a message to a specific client """
		cmd = Command(command, *args, id='UNICAST')
		socket.send(str(cmd) + self._split)
	
	def broadcast(self, command, *args):
		""" Send a message to all connected clients """
		cmd = Command(command, *args, id='BROADCAST')
		for c in self.clients.keys():
			try:
				c.send(str(cmd) + self._split)
			except socket.error:
				del self.clients[c]

	def tick(self):
		self.tick_counter+=1
		key_tick=False
		if(self.tick_counter==15):
			key_tick=True
			self.tick_counter=0
		for p in self._players.values():
			p.tick(key_tick)
		for o in self.all_entities():
			o.tick(key_tick)

	def list_of_entities(self, connection):
		return [x.dinmamma() for x in self._entities.values()]

	def NewUser(self, connection, name, password):
		# verify
		if name in self._players:
			raise CommandError, 'Username already exists'
		
		# create
		p = player.Player(name, self)
		p.set_password(password)
		
		# store
		self.add_player(p)
		
		# push info to all players.
		self.broadcast('NEW_PLAYER', p.id, p.name)
		
		return 'OK'

	def playerinfo(self, connection, id):
		# try numerical ID
		try:
			p = self.player_by_id(int(id))
		except ValueError:
			p = self.player_by_username(id)
		
		if p is None:
			raise CommandError, 'Invalid ID'
		
		return p.info()

	def Players(self, connection):
		# dict comprehensions are not introduced until 2.7 =/
		return dict([(p.id, p.name) for p in self._players.values()])

	def login(self, connection, name, passwd):
		p = self.player_by_username(name)
		
		# validate credentials
		if p is None or not p.login(connection, passwd):
			raise CommandError, 'Invalid username or password'

		# store in connection as well
		connection.player = p
		
		# Send info to all players
		self.broadcast('USER_LOGIN', p.id, p.name)
		
		return "OK ID=%d" % (p.id)

	def EntAction(self, connection, id, action, *args):
		ent = self.entity_by_id(id)
		if ent is None:
			raise CommandError, 'Invalid ID'
		
		player = connection.player
		if not ent in player.entities:
			raise CommandError, 'Belongs to other player'

		response = ent.action(action, args)
		self.player_persist()
		
		return response
