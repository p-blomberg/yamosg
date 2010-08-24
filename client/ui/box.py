#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
import functools
from common.vector import Vector3

class _Box:
      def __init__(self, position=Vector3(0,0,0), size=Vector3(0,0,0), *widgets):
            self.pos = position.copy()
            self.size = size.copy()
            self._widgets = []
            for c in widgets:
                  self.add(c)

      def _default_size(self, size, field):
            # get the sum of the requested widths
            n = 0
            sum = 0.0
            for _, wsize, _ in self._widgets:
                  if wsize is None:
                        n += 1
                        continue

                  abs = wsize.get_absolute(size)
                  sum += getattr(abs, field)

            left = float(getattr(size, field) - sum)

            if left <= 0 or n == 0:
                  return 0
            
            return left / n

      def _resize_children(self, size, dx=None, dy=None):
            x = 0.0
            y = 0.0
            for n, (widget, wsize, wposition) in enumerate(self._widgets):
                  widget.pos.x = x
                  widget.pos.y = y
                  widget.pos.z = 0.0

                  if wsize is None:
                        ix = dx
                        iy = dy
                        widget.size.x = dx or size.x
                        widget.size.y = dy or size.y
                  else:
                        abs = wsize.get_absolute(size)
                        ix = abs.x
                        iy = abs.y
                        widget.size = abs

                  # increase position
                  if dx is not None:
                        x += ix
                  if dy is not None:
                        y += iy

                  widget.on_resize(widget.size)

      def is_invalidated(self):
            return any([x.is_invalidated() for x in self.get_children()])

      def get_children(self):
            return [widget for (widget, _, _) in self._widgets]

      def render(self):
            for x in self.get_children():
                  glPushMatrix()
                  x.render()
                  glPopMatrix()

      def display(self):
            glTranslatef(*self.pos)
            for c in self.get_children():
                  glPushMatrix()
                  c.display()
                  glPopMatrix()

      def add(self, widget, size=None, position=None):
            self._widgets.append((widget, size, position))

class HBox(_Box):
      def __init__(self, *widgets):
            _Box.__init__(self, *widgets)
            self._default_size = functools.partial(_Box._default_size, self, field='x')

      def on_resize(self, size):
            self.size = size
            delta = self._default_size(size)
            self._resize_children(size, dx=delta)

class VBox(_Box):
      def __init__(self, *widgets):
            _Box.__init__(self, *widgets)
            self._default_size = functools.partial(_Box._default_size, self, field='y')

      def on_resize(self, size):
            self.size = size
            delta = self._default_size(size)
            self._resize_children(size, dy=delta)
