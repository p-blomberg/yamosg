#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
import functools
from common.vector import Vector3, Vector2i
from ui import Widget
from ui.container import Container

class _Box(Container, Widget):
      def __init__(self, position=Vector3(0,0,0), size=Vector2i(1,1), *widgets):
            Container.__init__(self, children=widgets)
            Widget.__init__(self, position, size)

      def _default_size(self, size, field):
            # get the sum of the requested widths
            n = 0
            sum = 0.0
            for widget in self.get_children():
                  if widget.__size is None:
                        n += 1
                        continue

                  abs = widget.__size.get_absolute(size)
                  sum += getattr(abs, field)

            left = float(getattr(size, field) - sum)

            if left <= 0 or n == 0:
                  return 0
            
            return left / n

      def _resize_children(self, size, final, dx=None, dy=None):
            x = 0.0
            y = 0.0
            for n, widget in enumerate(self.get_children()):
                  widget.pos.x = x
                  widget.pos.y = y
                  widget.pos.z = 0.0

                  if widget.__size is None:
                        ix = dx
                        iy = dy
                        widget.size.x = dx or size.x
                        widget.size.y = dy or size.y
                  else:
                        abs = widget.__size.get_absolute(size)
                        ix = abs.x
                        iy = abs.y
                        widget.size = abs

                  # increase position
                  if dx is not None:
                        x += ix
                  if dy is not None:
                        y += iy

                  widget.on_resize(widget.size, final)

      def add(self, widget, size=None, position=None):
            widget.__size = size
            widget.__position = position
            Container.add(self, widget)

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

class HBox(_Box):
      def __init__(self, *widgets):
            _Box.__init__(self, *widgets)
            self._default_size = functools.partial(_Box._default_size, self, field='x')

      def on_resize(self, size, final):
            _Box.on_resize(self, size, final)
            delta = self._default_size(size)
            self._resize_children(size, final, dx=delta)

class VBox(_Box):
      def __init__(self, *widgets):
            _Box.__init__(self, *widgets)
            self._default_size = functools.partial(_Box._default_size, self, field='y')

      def on_resize(self, size, final):
            _Box.on_resize(self, size, final)
            delta = self._default_size(size)
            self._resize_children(size, final, dy=delta)
