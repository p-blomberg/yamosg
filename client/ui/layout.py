#!/usr/bin/python
# -*- coding: utf-8 -*-

class LayoutAttachment:
    def __init__(self, relative, absolute):
        """"
        Layout attachment request, the container may or may not conform to the request.

        :param relative: Percentage of container.
        :param absolute: Pixel offset.
        """

        self.relative = relative
        self.absolute = absolute

    def get_absolute(self, size):
        return self.relative * size + self.absolute

        
