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

def encoder(name, *args, **kwargs):
	return _encoders[name](*args, **kwargs)

def decoder(name, *args, **kwargs):
	return _decoders[name](*args, **kwargs)

def encoders():
	return _encoders.keys()

def decoders():
	return _decoders.keys()

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
