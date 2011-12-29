from serversocket import Connection
from common.transcoder import encoder
from common.error import *
import traceback
import functools

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
			"PLAYERS": self.game.Players,
			"QUIT": self.game.logout
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

	@staticmethod
	def _unknown_command(*args, **kwargs):
		raise CommandError("I don't know the command %s" % kwargs['cmd'])
	
	def command(self, cmd, args):
		func = self._commands.get(cmd, functools.partial(self._unknown_command, cmd=cmd))
		
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
