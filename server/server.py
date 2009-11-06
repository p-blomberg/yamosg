class Server(gnitset_sockets.ServerSocket):
	def __init__(self, host, port, timeout=30, split="\n", debug=False):
		sockets.ServerSocket.__init__(self, host, port, timeout, split, debug)

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

