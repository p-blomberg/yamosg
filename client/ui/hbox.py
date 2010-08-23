#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *

class HBox:
      def __init__(self, *widgets):
            self._widgets = []
            for c in widgets:
                  self.add(c)

      def is_invalidated(self):
            return any([x.is_invalidated() for x in self.get_children()])

      def get_children(self):
            return [widget for (widget, _, _) in self._widgets]
      
      def on_resize(self, size):
            dx = float(size.x) / len(self._widgets)
            for n, (widget, wsize, wposition) in enumerate(self._widgets):
                  widget.pos.y = 00
                  widget.pos.x = n*dx
                  widget.pos.z = 0.0
                  widget.size.x = dx
                  widget.size.y = size.y
                  widget.on_resize(widget.size)

      def render(self):
            for x in self.get_children():
                  glPushMatrix()
                  x.render()
                  glPopMatrix()

      def display(self):
            for c in self.get_children():
                  c.display()

      def add(self, widget, size=None, position=None):
            self._widgets.append((widget, size, position))
