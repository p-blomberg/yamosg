'''OpenGL extension SGIS.texture4D

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_SGIS_texture4D'
_DEPRECATED = False
GL_PACK_SKIP_VOLUMES_SGIS = constant.Constant( 'GL_PACK_SKIP_VOLUMES_SGIS', 0x8130 )
GL_PACK_IMAGE_DEPTH_SGIS = constant.Constant( 'GL_PACK_IMAGE_DEPTH_SGIS', 0x8131 )
GL_UNPACK_SKIP_VOLUMES_SGIS = constant.Constant( 'GL_UNPACK_SKIP_VOLUMES_SGIS', 0x8132 )
GL_UNPACK_IMAGE_DEPTH_SGIS = constant.Constant( 'GL_UNPACK_IMAGE_DEPTH_SGIS', 0x8133 )
GL_TEXTURE_4D_SGIS = constant.Constant( 'GL_TEXTURE_4D_SGIS', 0x8134 )
GL_PROXY_TEXTURE_4D_SGIS = constant.Constant( 'GL_PROXY_TEXTURE_4D_SGIS', 0x8135 )
GL_TEXTURE_4DSIZE_SGIS = constant.Constant( 'GL_TEXTURE_4DSIZE_SGIS', 0x8136 )
GL_TEXTURE_WRAP_Q_SGIS = constant.Constant( 'GL_TEXTURE_WRAP_Q_SGIS', 0x8137 )
GL_MAX_4D_TEXTURE_SIZE_SGIS = constant.Constant( 'GL_MAX_4D_TEXTURE_SIZE_SGIS', 0x8138 )
GL_TEXTURE_4D_BINDING_SGIS = constant.Constant( 'GL_TEXTURE_4D_BINDING_SGIS', 0x814F )
glTexImage4DSGIS = platform.createExtensionFunction( 
'glTexImage4DSGIS',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLenum,constants.GLint,constants.GLenum,constants.GLsizei,constants.GLsizei,constants.GLsizei,constants.GLsizei,constants.GLint,constants.GLenum,constants.GLenum,ctypes.c_void_p,),
doc='glTexImage4DSGIS(GLenum(target), GLint(level), GLenum(internalformat), GLsizei(width), GLsizei(height), GLsizei(depth), GLsizei(size4d), GLint(border), GLenum(format), GLenum(type), c_void_p(pixels)) -> None',
argNames=('target','level','internalformat','width','height','depth','size4d','border','format','type','pixels',),
deprecated=_DEPRECATED,
)

glTexSubImage4DSGIS = platform.createExtensionFunction( 
'glTexSubImage4DSGIS',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLenum,constants.GLint,constants.GLint,constants.GLint,constants.GLint,constants.GLint,constants.GLsizei,constants.GLsizei,constants.GLsizei,constants.GLsizei,constants.GLenum,constants.GLenum,ctypes.c_void_p,),
doc='glTexSubImage4DSGIS(GLenum(target), GLint(level), GLint(xoffset), GLint(yoffset), GLint(zoffset), GLint(woffset), GLsizei(width), GLsizei(height), GLsizei(depth), GLsizei(size4d), GLenum(format), GLenum(type), c_void_p(pixels)) -> None',
argNames=('target','level','xoffset','yoffset','zoffset','woffset','width','height','depth','size4d','format','type','pixels',),
deprecated=_DEPRECATED,
)


def glInitTexture4DSGIS():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
