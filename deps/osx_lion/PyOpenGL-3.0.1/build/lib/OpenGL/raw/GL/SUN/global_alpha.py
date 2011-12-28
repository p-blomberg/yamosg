'''OpenGL extension SUN.global_alpha

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_SUN_global_alpha'
_DEPRECATED = False
GL_GLOBAL_ALPHA_SUN = constant.Constant( 'GL_GLOBAL_ALPHA_SUN', 0x81D9 )
GL_GLOBAL_ALPHA_FACTOR_SUN = constant.Constant( 'GL_GLOBAL_ALPHA_FACTOR_SUN', 0x81DA )
glget.addGLGetConstant( GL_GLOBAL_ALPHA_FACTOR_SUN, (1,) )
glGlobalAlphaFactorbSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactorbSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLbyte,),
doc='glGlobalAlphaFactorbSUN(GLbyte(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactorsSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactorsSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLshort,),
doc='glGlobalAlphaFactorsSUN(GLshort(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactoriSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactoriSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLint,),
doc='glGlobalAlphaFactoriSUN(GLint(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactorfSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactorfSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLfloat,),
doc='glGlobalAlphaFactorfSUN(GLfloat(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactordSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactordSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLdouble,),
doc='glGlobalAlphaFactordSUN(GLdouble(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactorubSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactorubSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLubyte,),
doc='glGlobalAlphaFactorubSUN(GLubyte(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactorusSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactorusSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLushort,),
doc='glGlobalAlphaFactorusSUN(GLushort(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)

glGlobalAlphaFactoruiSUN = platform.createExtensionFunction( 
'glGlobalAlphaFactoruiSUN',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,),
doc='glGlobalAlphaFactoruiSUN(GLuint(factor)) -> None',
argNames=('factor',),
deprecated=_DEPRECATED,
)


def glInitGlobalAlphaSUN():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
