#!/usr/bin/python
# -*- coding: utf-8 -*-

class BaseEncoder:
	def encode(self, item):
		raise NotImplementedError

class BaseDecoder:
	def decode(self, item):
		raise NotImplementedError
