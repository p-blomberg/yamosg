'''OpenGL extension VERSION.GL_1_3

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_1_3 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_1_3.txt
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.VERSION.GL_1_3 import *
### END AUTOGENERATED SECTION
from OpenGL.GL.VERSION.GL_1_3_images import *

for typ,arrayType in (
    ('d',arrays.GLdoubleArray),
    ('f',arrays.GLfloatArray),
    ('i',arrays.GLintArray),
    ('s',arrays.GLshortArray),
):
    for size in (1,2,3,4):
        name = 'glMultiTexCoord%(size)s%(typ)sv'%globals()
        globals()[name] = arrays.setInputArraySizeType(
            globals()[name],
            size,
            arrayType, 
            'v',
        )
        del size,name
    del typ,arrayType

for typ,arrayType in (
    ('d',arrays.GLdoubleArray),
    ('f',arrays.GLfloatArray),
):
    for function in ('glLoadTransposeMatrix','glMultTransposeMatrix'):
        name = '%s%s'%(function,typ)
        globals()[name] = arrays.setInputArraySizeType(
            globals()[name],
            16,
            arrayType, 
            'm',
        )
        del function,name
    del typ,arrayType