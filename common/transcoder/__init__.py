#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module aids with the line encoding and decoding. It supports multiple
encoders like plaintext and json. Plaintext is the default and is suitable for
telnet clients.
'''

import _plaintext
import _jsoncoder

_encoders = {
	'plaintext': _plaintext.Encoder,
	'json': _jsoncoder.Encoder
}

_decoders = {
	'plaintext': _plaintext.Decoder,
	'json': _jsoncoder.Decoder
}

def _factory(name, src, args, kwargs):
	try:
		return src[name](*args, **kwargs)
	except KeyError:
		return None

def encoder(name, *args, **kwargs):
	return _factory(name, _encoders, args, kwargs)

def decoder(name, *args, **kwargs):
	return _factory(name, _decoders, args, kwargs)

if __name__ == '__main__':
	e = encoder('plaintext')
	print e.encode({
		'foo': 'bar',
		'fred': 3**4,
		'barney': {
			'spam': 'bacon',
			'wilma': [1,3,3,7]
		}
	})
