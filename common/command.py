#!/usr/bin/python
# -*- coding: utf-8 -*-

import shlex, threading

def parse(line):
	"""
	parse(line) -> (command, ([arg0], ...))
	Parse a protocol command.
	"""
	
	# Tokenize
	tokens = shlex.split(line)
	
	# Simple validation
	if len(tokens) < 2:
		raise RuntimeError, 'Unable to parse command: ' + str([line])
	
	# Extract counter
	counter = tokens.pop(0)

	# Extract command
	cmd = tokens.pop(0)

	return counter, cmd, tuple(tokens)

def parse_tokens(line):
	return shlex.split(line)

class Command:
	""" Represents a protocol command """
	_id = 0
	
	def __init__(self, command, *args, **kwargs):
		"""
		All args are quoted as neccesary.
		Pass kwarg id to use a specific id
		"""
		
		self.command = command
		self.args = args
		self._reply = None
		self._event = None
		
		# check if a specific id was requested, eg broadcast
		if 'id' in kwargs:
			self.id = kwargs['id']
		else:
			# autogenerate id
			self.id = Command._id
			Command._id += 1
		
		# force it to be a string
		self.id = str(self.id)
	
	def __str__(self):
		# convert to string and quote if it contains a space.
		def quote(x):
			if ' ' in x:
				return '"%s"' % x
			if x == '':
				return '""'
			return x
		
		return '{id} {cmd} {args}'.format(id=self.id, cmd=self.command, args=' '.join([quote(str(x).replace('"', '\\"')) for x in self.args]))
	
	def reply(self, status, args, line):
		""" Mark that this command has recieved a reply """
		self._reply = (status, args, line)
		if self._event is not None:
			self._event.set()
	
	def wait(self):
		self._event = threading.Event()
		self._event.wait()
		return self.get_reply()
	
	def get_reply(self):
		return self._reply
