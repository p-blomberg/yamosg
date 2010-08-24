#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
import functools

class _Box:
      def __init__(self, *widgets):
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

            left = float(size.x - sum)

            if left <= 0 or n == 0:
                  return 0
            
            return left / n

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
            for c in self.get_children():
                  glPushMatrix()
                  c.display()
                  glPopMatrix()

      def add(self, widget, size=None, position=None):
            self._widgets.append((widget, size, position))

class HBox(_Box):
      _default_size = functools.partial(_Box._default_size, field='x')

      def __init__(self, *widgets):
            _Box.__init__(self, *widgets)

      def on_resize(self, size):
            dx = self._default_size(self, size)
            x = 0.0
            for n, (widget, wsize, wposition) in enumerate(self._widgets):
                  widget.pos.y = 00
                  widget.pos.x = x
                  widget.pos.z = 0.0

                  if wsize is None:
                        x += dx
                        widget.size.x = dx
                        widget.size.y = size.y
                  else:
                        abs = wsize.get_absolute(size)
                        x += abs.x
                        widget.size = abs

                  widget.on_resize(widget.size)
