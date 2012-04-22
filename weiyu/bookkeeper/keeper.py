#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / central bookkeeper / classes
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

u'''
Bookkeepers
~~~~~~~~~~~

This module provides classes for global bookkeeping.

'''

from __future__ import unicode_literals, division

import abc

__all__ = ['BookkeeperBase',
           'UnicodeBookkeeper',
           'FunctionBookkeeper',
           ]


class BookkeeperBase(object):
    '''A simple bookkeeper base class with a ``dict``-like interface.

    The bookkeepers are meant for use as global singleton instances, keeping
    record of various components/preferences. The keys

    The class is abstract, thus *not* directly usable. You must subclass
    and override its ``normalize_key`` method, which is used to convert
    keys into a unified type.

    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.__registry = {}

    @abc.abstractmethod
    def normalize_key(self, key):
        pass

    def register(self, key, value):
        normalized_key = self.normalize_key(key)

        if normalized_key in self.__registry:
            raise AttributeError("'%s' is already registered with value '%s'"
                                 % (repr(typed_key), repr(value), )
                                 )

        self.__registry[normalized_key] = value

    def unregister(self, key):
        normalized_key = self.normalize_key(key)

        try:
            return self.__registry.pop(normalized_key)
        except KeyError:
            raise KeyError("key '%s' not registered" % repr(normalized_key))

    def __getitem__(self, key):
        return self.__registry[self.normalize_key(key)]


class UnicodeBookkeeper(BookkeeperBase):
    def normalize_key(self, key):
        return unicode(key)


class FunctionBookkeeper(UnicodeBookkeeper):
    '''Bookkeeper for registering functions.'''

    def register(self, name=None):
        '''Convenient decorator for registering functions.

        If  ``name`` is ``None``, the function's ``func_name`` is used as
        key. Otherwise the name specified is used.

        .. note::
            To use function names, the decorator must be used with parens
            like ``@registry.register()``, or the function won't be executed.

        '''

        def _decorator_(fn):
            key = fn.func_name if name is None else name
            super(FunctionBookkeeper, self).register(key, fn)

            return fn

        return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
