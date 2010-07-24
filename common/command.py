#!/usr/bin/python
# -*- coding: utf-8 -*-

import shlex

def parse(line, split="\n"):
	"""
	parse(line) -> (command, ([arg0], ...))
	Parse a protocol command.
	"""
	
	# Remove split
	# @todo verify that split is actually there.
	n = len(split)
	line = line[:-n]
	
	# Tokenize
	tokens = shlex.split(line)
	
	# Extract counter
	counter = tokens.pop(0)

	# Extract command
	cmd = tokens.pop(0)

	return counter, cmd, tuple(tokens)

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
			x = str(x)
			if ' ' in x:
				return '"%s"' % x
			else:
				return x
		
		return '{id} {cmd} {args}'.format(id=self.id, cmd=self.command, args=' '.join([quote(x) for x in self.args]))
	
	def reply(self, command, args):
		""" Mark that this command has recieved a reply """
		self._reply = (command, args)
	
	def get_reply(self):
		return self._reply
