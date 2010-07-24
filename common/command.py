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
	
	# Extract command
	cmd = tokens.pop(0)
	return cmd, tuple(tokens)
