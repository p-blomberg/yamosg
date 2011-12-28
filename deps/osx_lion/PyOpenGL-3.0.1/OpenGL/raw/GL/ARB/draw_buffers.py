'''OpenGL extension ARB.draw_buffers

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_ARB_draw_buffers'
_DEPRECATED = False
GL_MAX_DRAW_BUFFERS_ARB = constant.Constant( 'GL_MAX_DRAW_BUFFERS_ARB', 0x8824 )
glget.addGLGetConstant( GL_MAX_DRAW_BUFFERS_ARB, (1,) )
GL_DRAW_BUFFER0_ARB = constant.Constant( 'GL_DRAW_BUFFER0_ARB', 0x8825 )
glget.addGLGetConstant( GL_DRAW_BUFFER0_ARB, (1,) )
GL_DRAW_BUFFER1_ARB = constant.Constant( 'GL_DRAW_BUFFER1_ARB', 0x8826 )
glget.addGLGetConstant( GL_DRAW_BUFFER1_ARB, (1,) )
GL_DRAW_BUFFER2_ARB = constant.Constant( 'GL_DRAW_BUFFER2_ARB', 0x8827 )
glget.addGLGetConstant( GL_DRAW_BUFFER2_ARB, (1,) )
GL_DRAW_BUFFER3_ARB = constant.Constant( 'GL_DRAW_BUFFER3_ARB', 0x8828 )
glget.addGLGetConstant( GL_DRAW_BUFFER3_ARB, (1,) )
GL_DRAW_BUFFER4_ARB = constant.Constant( 'GL_DRAW_BUFFER4_ARB', 0x8829 )
glget.addGLGetConstant( GL_DRAW_BUFFER4_ARB, (1,) )
GL_DRAW_BUFFER5_ARB = constant.Constant( 'GL_DRAW_BUFFER5_ARB', 0x882A )
glget.addGLGetConstant( GL_DRAW_BUFFER5_ARB, (1,) )
GL_DRAW_BUFFER6_ARB = constant.Constant( 'GL_DRAW_BUFFER6_ARB', 0x882B )
glget.addGLGetConstant( GL_DRAW_BUFFER6_ARB, (1,) )
GL_DRAW_BUFFER7_ARB = constant.Constant( 'GL_DRAW_BUFFER7_ARB', 0x882C )
glget.addGLGetConstant( GL_DRAW_BUFFER7_ARB, (1,) )
GL_DRAW_BUFFER8_ARB = constant.Constant( 'GL_DRAW_BUFFER8_ARB', 0x882D )
glget.addGLGetConstant( GL_DRAW_BUFFER8_ARB, (1,) )
GL_DRAW_BUFFER9_ARB = constant.Constant( 'GL_DRAW_BUFFER9_ARB', 0x882E )
glget.addGLGetConstant( GL_DRAW_BUFFER9_ARB, (1,) )
GL_DRAW_BUFFER10_ARB = constant.Constant( 'GL_DRAW_BUFFER10_ARB', 0x882F )
glget.addGLGetConstant( GL_DRAW_BUFFER10_ARB, (1,) )
GL_DRAW_BUFFER11_ARB = constant.Constant( 'GL_DRAW_BUFFER11_ARB', 0x8830 )
glget.addGLGetConstant( GL_DRAW_BUFFER11_ARB, (1,) )
GL_DRAW_BUFFER12_ARB = constant.Constant( 'GL_DRAW_BUFFER12_ARB', 0x8831 )
glget.addGLGetConstant( GL_DRAW_BUFFER12_ARB, (1,) )
GL_DRAW_BUFFER13_ARB = constant.Constant( 'GL_DRAW_BUFFER13_ARB', 0x8832 )
glget.addGLGetConstant( GL_DRAW_BUFFER13_ARB, (1,) )
GL_DRAW_BUFFER14_ARB = constant.Constant( 'GL_DRAW_BUFFER14_ARB', 0x8833 )
glget.addGLGetConstant( GL_DRAW_BUFFER14_ARB, (1,) )
GL_DRAW_BUFFER15_ARB = constant.Constant( 'GL_DRAW_BUFFER15_ARB', 0x8834 )
glget.addGLGetConstant( GL_DRAW_BUFFER15_ARB, (1,) )
glDrawBuffersARB = platform.createExtensionFunction( 
'glDrawBuffersARB',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLsizei,arrays.GLuintArray,),
doc='glDrawBuffersARB(GLsizei(n), GLuintArray(bufs)) -> None',
argNames=('n','bufs',),
deprecated=_DEPRECATED,
)


def glInitDrawBuffersARB():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
