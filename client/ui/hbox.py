#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *

class HBox:
      def __init__(self, *widgets):
      	  self._widgets = widgets

      def is_invalidated(self):
            return any([x.is_invalidated() for x in self.get_children()])

      def get_children(self):
            return self._widgets
      
      def on_resize(self, size):
            #dx = float(size.x) / len(self._widgets)
            dx = 25.0
            for n,c in enumerate(self._widgets):
                  print n, n*dx
                  c.pos.y = 00
                  c.pos.x = n*dx
                  c.pos.z = 0.0
                  c.size.x = dx
                  c.size.y = size.y
                  c.on_resize(c.size)

      def render(self):
            for x in self.get_children():
                  glPushMatrix()
                  x.render()
                  glPopMatrix()

      def display(self):
            for c in self._widgets:
                  c.display()
