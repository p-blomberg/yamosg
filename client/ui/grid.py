#!/usr/bin/python
# -*- coding: utf-8 -*-

from ui import Widget
from ui.container import Container

from OpenGL.GL import *

class Grid(Container, Widget):
    def __init__(self, columns, rows, *widgets):
        Container.__init__(self, children=widgets)
        Widget.__init__(self)
        self._cols = int(columns)
        self._rows = int(rows)
    
    def render(self):
        for x in self.get_children():
            glPushMatrix()
            x.render()
            glPopMatrix()

    def display(self):
        glTranslatef(*self.pos)
        for x in self.get_children():
            glPushMatrix()
            x.display()
            glPopMatrix()
    
    def on_resize(self, size):
        Widget.on_resize(self, size)
        
        dx, dy = size * (1.0/self._cols, 1.0/self._rows)

        x = 0.0
        y = 0.0
        for n, widget in enumerate(self.get_children()):
            widget.pos.x = (n%self._cols) * dx
            widget.pos.y = (n/self._cols) * dy
            widget.pos.z = 0.0
            
            widget.size.x = dx
            widget.size.y = dy

            widget.on_resize(widget.size)
