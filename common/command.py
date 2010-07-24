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
	_id = 0
	
	def __init__(self, command, *args, **kwargs):
		self.command = command
		self.args = args
		self._reply = None
		
		if 'id' in kwargs:
			self.id = id
		else:
			self.id = Command._id
			Command._id += 1
		
		# force it to be a string
		self.id = str(self.id)
	
	def __str__(self):
		def quote(x):
			if ' ' in x:
				return '"%s"' % str(x)
			else:
				return str(x)
		
		return '{id} {cmd} {args}'.format(id=self.id, cmd=self.command, args=[quote(x) for x in self.args])
	
	def reply(self, command, args):
		self._reply = (command, args)
	
	def get_reply(self):
		return self._reply
