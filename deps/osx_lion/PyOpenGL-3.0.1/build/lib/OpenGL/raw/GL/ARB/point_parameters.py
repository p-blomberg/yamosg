'''OpenGL extension ARB.point_parameters

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_ARB_point_parameters'
_DEPRECATED = False
GL_POINT_SIZE_MIN_ARB = constant.Constant( 'GL_POINT_SIZE_MIN_ARB', 0x8126 )
glget.addGLGetConstant( GL_POINT_SIZE_MIN_ARB, (1,) )
GL_POINT_SIZE_MAX_ARB = constant.Constant( 'GL_POINT_SIZE_MAX_ARB', 0x8127 )
glget.addGLGetConstant( GL_POINT_SIZE_MAX_ARB, (1,) )
GL_POINT_FADE_THRESHOLD_SIZE_ARB = constant.Constant( 'GL_POINT_FADE_THRESHOLD_SIZE_ARB', 0x8128 )
glget.addGLGetConstant( GL_POINT_FADE_THRESHOLD_SIZE_ARB, (1,) )
GL_POINT_DISTANCE_ATTENUATION_ARB = constant.Constant( 'GL_POINT_DISTANCE_ATTENUATION_ARB', 0x8129 )
glget.addGLGetConstant( GL_POINT_DISTANCE_ATTENUATION_ARB, (3,) )
glPointParameterfARB = platform.createExtensionFunction( 
'glPointParameterfARB',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLenum,constants.GLfloat,),
doc='glPointParameterfARB(GLenum(pname), GLfloat(param)) -> None',
argNames=('pname','param',),
deprecated=_DEPRECATED,
)

glPointParameterfvARB = platform.createExtensionFunction( 
'glPointParameterfvARB',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLenum,arrays.GLfloatArray,),
doc='glPointParameterfvARB(GLenum(pname), GLfloatArray(params)) -> None',
argNames=('pname','params',),
deprecated=_DEPRECATED,
)


def glInitPointParametersARB():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )