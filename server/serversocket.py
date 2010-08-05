#! /usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import signal
import sys
import traceback
import errno
from select import select

def have_trailing_newline(line):
	""" Check if a line has a trailing newline """
	return line[-1] == '\n' or line[-1] == '\r' or line[-2:] == '\r\n'

class Connection:
	def __init__(self, sock, server):
		self._socket = sock
		self._peer   = sock.getpeername()
		self._server = server
		
		self._writequeue = []
		self._readbuffer = ''
	
	def peer(self):
		""" Get string representation of this connection, eg ip """
		return self._peer
	
	def fileno(self):
		""" So the instances fits to select """
		return self._socket.fileno()
	
	def disconnect(self, message):
		""" Disconnect this connection """
		
		# Flush outgoing data first
		try:
			self._flush()
		except socket.error:
			# there is nothing to be done, this cannot be handled
			pass
		
		# Mark as shutdown
		try:
			self._socket.shutdown(socket.SHUT_RDWR)
		except socket.error:
			pass
		
		# Remove from storage
		self._server._del_client(self, message)
	
	def write(self, chunk):
		self._writequeue.append(chunk)
	
	def _read(self):
		try:
			data = self._socket.recv(8192)
		except socket.error:
			self.disconnect('socket unexpectedly closed')
			return
		
		if not data:
			self.disconnect('socket unexpectedly closed')
			return
		
		# if the previous recv only got a partial line it was
		# stored and will be appended to this recv.
		if self._readbuffer:
			data = self._readbuffer + data
			self._readbuffer = None

		lines = data.splitlines()
		
		# store tail
		if not have_trailing_newline(data):
			tail = lines.pop()
			self._readbuffer = tail

		for line in lines:
			yield line
	
	def _flush(self):
		""" Send all queued data for socket """
		
		for element in self._writequeue:
			size = len(element)
			while size > 0:
				try:
					sent = self._socket.send(element)
					element = element[sent:]
					size -= sent
				except socket.error, e:
					if e.errno == errno.EAGAIN:
						continue
					raise
		
		self._writequeue = []

class ServerSocket:
	connection_object = Connection
	
	def __init__(self, host, port, timeout=30):
		signal.signal(signal.SIGINT, self.quit)
		self._timeout = timeout

		# connected clients
		self._clients = []

		# listen socket
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._socket.bind((host, port))
		self._socket.listen(5)
	
	def new_connection(self, connection):
		""" Called when a new connection has been accepted """
		pass # do nothing
	
	def lost_connection(self, connection, message):
		""" Called when a connection is lost (expected or not) """
		pass # do nothing
	
	def _add_client(self, sock):
		""" Store client, and notify that a new client has connected. """
		# create new connection object
		connection = self.connection_object(sock, self)
		
		# store and notify
		self._clients.append(connection)
		self.new_connection(connection)
	
	def _del_client(self, connection, reason=None):
		""" Delete a client from storage, and notify of this. """
		self._clients.remove(connection)
		self.lost_connection(connection, reason)
	
	def clients(self):
		""" Get all clients. Generator """
		for client in self._clients:
			yield client

	def checkSockets(self):
		""" Poll the sockets for updates """
		
		rlist = [self._socket] + self._clients
		wlist = self._clients
		xlist = self._clients
		
		try:
			read, write, error = select(rlist, wlist, xlist, self._timeout)

			# see if listen socket is ready to accept
			if self._socket in read:
				# add client
				(clientsocket, _) = self._socket.accept()
				self._add_client(clientsocket)
				
				# remove listen socket from ready list
				read.remove(self._socket)

			# Flush all clients that are ready.
			for client in write:
				client._flush()

			# Read data from clients that have sent data
			for client in read:
				for line in client._read():
					self.readCall(client, line)
			
			# Socket exceptions
			for client in error:
				client.disconnect('socket exception')
		
		except SystemExit:
			raise
		except:
			traceback.print_exc()

	def readCall(self, clientsocket, lines):
		""" Command callback """
		raise NotImplementedError
	
	def quit(self, signr, frame):
		""" Terminate server, all clients will be properly disconnected. """
		
		for client in self.clients():
			client.disconnect('server shutting down')
		
		try:
			self._socket.close()
		except socket.error:
			pass
		
		sys.exit()
