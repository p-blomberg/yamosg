#!/usr/bin/python
# -*- coding: utf-8; -*-

import logging

class Log(logging.LoggerAdapter):
	def __init__(self, name=None):
		logging.LoggerAdapter.__init__(self, logging.getLogger(name), {'peer': '-'})

class LogPeer(logging.LoggerAdapter):
	def __init__(self, name):
		logging.LoggerAdapter.__init__(self, logging.getLogger(name), {})

	def process(self, peer, msg, kwargs):
		kwargs['extra'] = {'peer': peer}
		return msg, kwargs

	def debug(self, peer, msg, *args, **kwargs):
		msg, kwargs = self.process(peer, msg, kwargs)
		self.logger.debug(msg, *args, **kwargs)

	def info(self, peer, msg, *args, **kwargs):
		msg, kwargs = self.process(peer, msg, kwargs)
		self.logger.info(msg, *args, **kwargs)

	def warning(self, peer, msg, *args, **kwargs):
		msg, kwargs = self.process(peer, msg, kwargs)
		self.logger.warning(msg, *args, **kwargs)

	def error(self, peer, msg, *args, **kwargs):
		msg, kwargs = self.process(peer, msg, kwargs)
		self.logger.error(msg, *args, **kwargs)
