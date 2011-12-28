'''OpenGL extension INGR.palette_buffer

This module customises the behaviour of the 
OpenGL.raw.GL.INGR.palette_buffer to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/INGR/palette_buffer.txt
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.INGR.palette_buffer import *
### END AUTOGENERATED SECTION