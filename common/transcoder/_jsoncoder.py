#!/usr/bin/python
# -*- coding: utf-8 -*-

from _base import BaseEncoder, BaseDecoder

import json

class Encoder(BaseEncoder):
	def encode(self, item):
		return json.dumps(item)

class Decoder(BaseDecoder):
	def decode(self, item):
		return json.loads(item)
