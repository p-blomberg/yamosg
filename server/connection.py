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

