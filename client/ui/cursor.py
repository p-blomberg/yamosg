from entity import load_sprite
from common.vector import Vector2i
from OpenGL.GL import *

class Cursor:
    def __init__(self, filename):
        self.sprite = load_sprite(filename)
        self.pos = Vector2i(0,0)

    def set_position(self, pos):
        self.pos = pos

    def render(self):
        glPushMatrix()
        glBindTexture(GL_TEXTURE_2D, self.sprite)
        glTranslatef(self.pos.x, self.pos.y, 0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0.25)
        glVertex3f(0, -32, 0)
        
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, 0)
        
        glTexCoord2f(0.25, 0)
        glVertex3f(32, 0, 0)
        
        glTexCoord2f(0.25, 0.25)
        glVertex3f(32, -32, 0)
        glEnd()
        
        glPopMatrix()
