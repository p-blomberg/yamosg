#!/usr/bin/python
# -*- coding: utf-8 -*-

from _base import BaseEncoder, BaseDecoder

import json

class Encoder(BaseEncoder):
	def encode(self, item, indent=0):
		return json.dumps(item, sort_keys=True, indent=2)

class Decoder(BaseDecoder):
	""" Not implemented since no one is supposed to decode the plaintext stream """
	pass
