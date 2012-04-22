#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / helpers / builder of path-like strings
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division

__all__ = ['PathBuilderBase', ]


class PathBuilderBase(object):
    '''Builder of path-like strings using Python attribute lookup syntax.

    Subclasses must define the class variable ``delim`` as a ``unicode``.
    That variable is the "path delimiter"; it is not allowed to appear in
    lookup attributes.

    '''

    def __init__(self, chain=None):
        if chain is None:
            self.__chain = []
        else:
            self.__chain = chain

    def __getattr__(self, att):
        att = unicode(att)
        if self.__class__.delim in att:
            raise AttributeError(u'no delimiters allowed in attribute name')
        return self.__class__(self.__chain + [att])

    def __unicode__(self):
        return (self.__class__.delim).join(self.__chain)

    def __repr__(self):
        return '<Path: %s>' % str(unicode(self))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
