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

from serversocket import ServerSocket, Connection
import entity
import player
from common.vector import Vector3
from common.command import Command
from common.transcoder import encoder, encoders
from common import command
import socket
import traceback
import json
import inspect

class CommandError (Exception):
	pass

class NoData (Exception):
	pass

def smart_truncate(content, length=100, suffix='...'):
	# Based on implementation found at:
	# http://stackoverflow.com/questions/250357/smart-truncate-in-python
	if len(content) <= length:
		return content
	else:
		return content[:length].rsplit(' ', 1)[0] + suffix

class Client (Connection):
	def __init__(self, sock, server, game):
		Connection.__init__(self, sock, server)
		
		self.game=game
		self.player=None
		self._encoder = encoder('plaintext')
		
		# client commands
		self._commands = {
			'SET': self._set_prop,
			"LOGIN": self.game.login,
			"LOGOUT": self.game.logout,
			"PING": self.ping,
			"PLAYERINFO": self.game.playerinfo,
			"NEWUSER": self.game.NewUser,
			"LIST_OF_ENTITIES": self.game.list_of_entities,
			"ENTINFO": self.game.entity_info,
			"ENTACTION": self.game.EntAction,
			"PLAYERS": self.game.Players
		}
		
		# properties
		self._props = {
			'ENCODER': self._set_encoder
		}
	
	def peer(self):
		if self.player:
			return str(Connection.peer(self)) + '::' + self.player.name
		else:
			return str(Connection.peer(self))
	
	def disconnect(self, message='Disconnected'):
		"""
		Force a client to disconnect.
		"""
		
		# notify client
		self.game.unicast(self, 'DISCONNECTED', message)
		
		# actual disconnect
		Connection.disconnect(self, message)
	
	def send(self, message):
		try:

			self.socket.send(message)
		except socket.error:
			traceback.print_exc()
			self._server.disconnect(self.socket)
		
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
		except NoData:
			# the client has been disconnected. Don't reply.
			return None
		except TypeError, e:
			# command didn't pass enought parameters.
			traceback.print_exc()
			return 'NOT_OK "%s"' % str(e)
		except:
			# an unhandled exception occured. Will not pass an specific details
			# to the client. 
			traceback.print_exc()
			return 'NOT_OK "An unexpected error occured. Try again later."'

class Server(ServerSocket):
	def _create_client(self, sock, server):
		return Client(sock, server, self.game)
	
	connection_object = _create_client
	
	def __init__(self, host, port, split="\n"):
		ServerSocket.__init__(self, host, port, 0)
		self._split = split
		self.game=Game(self)
		
		# Server commands
		self._commands = {
			'CAPS': self._get_caps
		}
		
		print "ready"
	
	def unicast(self, connection, command, *args):
		""" Send a message to a specific client """
		cmd = Command(command, *args, id='UNICAST')
		connection.write(str(cmd) + self._split)
	
	def broadcast(self, command, *args):
		""" Send a message to all connected clients """
		cmd = Command(command, *args, id='BROADCAST')
		for client in self.clients():
			client.write(str(cmd) + self._split)
	
	def new_connection(self, client):
		self.unicast(client , 'Hello')
	
	def lost_connection(self, client, message):
		p = client.player
		
		if p is not None:
			# forced disconnect
			
			p.logout(disconnected=True)
			
			# Send info to all players
			self.broadcast('USER_LOGOUT', p.id, p.name)
		
		print '{peer} disconnected: {message}'.format(peer=client.peer(), message=message)
	
	def readCall(self, client, line):
		response = self._dispatch_command(client, line)
		print '{peer} {line} -> {response}'.format(
			peer=client.peer(),
			line=[line], 
			response=response and [smart_truncate(str(response), length=50)]) or None
		
		if response is not None:
			client.write(response + self._split)
	
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
		
		# If the handler returned None, pass it directly. No data will be sent to the client.
		if response is None:
			return None
			
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

# decorators

def entity_param(param):
	"""
	Converts an entity id to an actual entity, raising CommandError if the id
	is invalid.
	"""
	
	def get_entity(self, id):
		ent = self.entity_by_id(id)
		if ent is None:
			raise CommandError, 'Invalid ID'
		return ent
	
	def outer(func):
		# locate the parameter
		arg_names = inspect.getargspec(func)[0]
		try:
			index = arg_names.index(param) - 1 # subtract 'self'
		except ValueError:
			raise SyntaxError, "'%s' is not a parameter of function '%s'" % (param, func.__name__)
		
		def inner(self, *args, **kwargs):
			# convert id -> entity
			args = list(args)
			args[index] = get_entity(self, args[index])
			
			# call function
			return func(self, *args, **kwargs)
		
		return inner
	return outer

class Game:
	def __init__(self, server):
		self._server=server
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
		p=entity.Planet(Vector3(30,30,0), 20, self)
		cargo={
			entity.CopperOre(container=p, owner=None, game=self): 600
		}
		p.cargo=cargo
		self.add_entity(p)
	
	def unicast(self, client, command, *args):
		self._server.unicast(client, command, *args)
	
	def broadcast(self, command, *args):
		self._server.broadcast(command, *args)
	
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
		return dict([(p.id, p.name) for p in self._players.values() if p.is_online()])

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
	
	def logout(self, connection):
		p = connection.player
		
		if p is None:
			# @TODO should still disconnect socket
			raise CommandError, 'Not logged in'
		
		# logout
		p.logout()
		
		# Send info to all players
		self.broadcast('USER_LOGOUT', p.id, p.name)
		
		# This is kind of hackish, but it assures that no reply is passed to
		# the (now) disconnected peer.
		raise NoData
	
	@entity_param('entity')
	def entity_info(self, connection, entity):
		print entity
	
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
