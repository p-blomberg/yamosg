#!/usr/bin/python
# -*- coding: utf-8; -*-

from common.logger import Log
import client
import traceback, json

network_log = Log('network')

def call(name, *args, **kwargs):
	global network_log, client
	
	decode = kwargs.get('decode', True)
	
	# pass command to server
	network_log.debug('calling %s(%s)', name, ', '.join([str(x) for x in args]))
	status, reply_args, line = client.call(name, *args)
	network_log.debug('reply: %s', line)

	if status != 'OK':
		raise RuntimeError, reply_args[0]

	# pass reply to callback
	try:
		if decode:
			decoded = None
			if line != '': # handle when servery reply is empty
				decoded = json.loads(line)
			return decoded
		
		return reply_args
	except:
		traceback.print_exc()
		print 'server reply was:', line
		return None

def typeinfo(id):
	return call('TYPEINFO', id)
