#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / hooking mechanism / central registry interaction
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
Hook information registry
~~~~~~~~~~~~~~~~~~~~~~~~~


'''

from __future__ import unicode_literals, division

from ..registry.classes import UnicodeRegistry
from ..registry.provider import request


def validate_hook_tuple(t):
    if not issubclass(type(t), tuple):
        raise ValueError('%s: not subclass of tuple' % repr(t))

    if len(t) != 2:
        raise ValueError('%s: length != 2' % repr(t))

    if not all(issubclass(type(lst), list) for lst in t):
        raise ValueError('%s: not all elements subclass of list' % repr(t))

    if not all(hasattr(item, '__call__') for lst in t for item in lst):
        raise ValueError('%s: non-callable item inside' % repr(t))


class HookRegistry(UnicodeRegistry):
    '''Registry for hooks.

    Key is the hook's name, while value is a 2-tuple of lists containing
    hook callables.

    '''

    def normalize_value(self, value):
        validate_hook_tuple(value)

        return value

# install a hook registry
try:
    import __builtin__
    __builtin__.__WEIYU_IN_SPHINX_AUTODOC
    del __builtin__
except AttributeError:
    request('weiyu.hooks', autocreate=True, klass=HookRegistry)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
