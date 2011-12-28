'''OpenGL extension ARB.vertex_array_object

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_ARB_vertex_array_object'
_DEPRECATED = False
GL_VERTEX_ARRAY_BINDING = constant.Constant( 'GL_VERTEX_ARRAY_BINDING', 0x85B5 )
glget.addGLGetConstant( GL_VERTEX_ARRAY_BINDING, (1,) )
glBindVertexArray = platform.createExtensionFunction( 
'glBindVertexArray',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,),
doc='glBindVertexArray(GLuint(array)) -> None',
argNames=('array',),
deprecated=_DEPRECATED,
)

glDeleteVertexArrays = platform.createExtensionFunction( 
'glDeleteVertexArrays',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLsizei,arrays.GLuintArray,),
doc='glDeleteVertexArrays(GLsizei(n), GLuintArray(arrays)) -> None',
argNames=('n','arrays',),
deprecated=_DEPRECATED,
)

glGenVertexArrays = platform.createExtensionFunction( 
'glGenVertexArrays',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLsizei,arrays.GLuintArray,),
doc='glGenVertexArrays(GLsizei(n), GLuintArray(arrays)) -> None',
argNames=('n','arrays',),
deprecated=_DEPRECATED,
)

glIsVertexArray = platform.createExtensionFunction( 
'glIsVertexArray',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=constants.GLboolean, 
argTypes=(constants.GLuint,),
doc='glIsVertexArray(GLuint(array)) -> constants.GLboolean',
argNames=('array',),
deprecated=_DEPRECATED,
)


def glInitVertexArrayObjectARB():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
