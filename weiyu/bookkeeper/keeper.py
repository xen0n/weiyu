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
Bookkeeper classes
~~~~~~~~~~~~~~~~~~

This module provides classes for global bookkeeping.

'''

from __future__ import unicode_literals, division

import abc
from types import FunctionType, MethodType

__all__ = ['BookkeeperBase',
           'UnicodeBookkeeper',
           'FunctionBookkeeper',
           'BookkeeperBookkeeper',
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
        '''Called to normalize any key passed in.

        Since the method is abstract, subclasses must override it.

        '''

        pass

    @abc.abstractmethod
    def normalize_value(self, value):
        '''Called to validate and normalize value before storing.

        If ``value`` does not validate (may be because of incorrect types,
        nonsense numerical value, etc), please raise ``ValueError``.

        This method is abstract too, so be sure to override this in your
        subclasses.

        '''

        pass

    def register(self, key, value):
        '''Register a key-value pair into the bookkeeper.
        '''

        normalized_key = self.normalize_key(key)

        if normalized_key in self.__registry:
            raise AttributeError(
                    "'%s' is already registered with value '%s'"
                    % (repr(typed_key), repr(value), )
                    )
        try:
            cooked_value = self.normalize_value(value)
        except ValueError:
            raise

        self.__registry[normalized_key] = cooked_value

    def unregister(self, key):
        '''Remove a previously registered entry.
        '''

        normalized_key = self.normalize_key(key)

        try:
            return self.__registry.pop(normalized_key)
        except KeyError:
            raise KeyError("key '%s' not registered" % repr(normalized_key))

    def __getitem__(self, key):
        return self.__registry[self.normalize_key(key)]


class UnicodeBookkeeper(BookkeeperBase):
    '''Bookkeeper with Unicode keys.

    As its name implies, this class is just ``BookkeeperBase`` with keys
    all converted to ``unicode``. Values can still be of any type though.

    '''

    def normalize_key(self, key):
        return unicode(key)

    def normalize_value(self, value):
        return value


class FunctionBookkeeper(UnicodeBookkeeper):
    '''Bookkeeper for registering functions.

    Note that ``register``'s signature is changed to make auto-registration
    on function definition more Pythonic, which is also the bookkeeper's
    desired usage pattern.

    '''

    def normalize_value(self, value):
        if type(value) not in (FunctionType, MethodType, ):
            raise ValueError("'%s': not a function" % (repr(value), ))

        return value

    def register(self, name=None):
        '''Convenient decorator for registering functions.

        If  ``name`` is ``None``, the function's ``func_name`` is used as
        key. Otherwise the name specified is used.

        .. note::
            To use function names, the decorator must be used with parens
            like ``@registry.register()``, or the decorator won't be
            executed.

        '''

        def _decorator_(fn):
            key = fn.func_name if name is None else name
            super(FunctionBookkeeper, self).register(key, fn)

            return fn

        return _decorator_


class BookkeeperBookkeeper(UnicodeBookkeeper):
    '''Bookkeeper for registering bookkeepers.

    In order to ensure true singleton pattern, all bookkeepers should be
    acquired from the central registry. Which explains why this very class
    exists...

    '''

    def normalize_value(self, value):
        if not issubclass(type(value), BookkeeperBase):
            raise ValueError("'%s': not a bookkeeper" % (repr(value), ))

        return value


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
