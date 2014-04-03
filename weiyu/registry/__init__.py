#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / central registry / package
#
# Copyright (C) 2012-2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

'''
Registry service provider
~~~~~~~~~~~~~~~~~~~~~~~~~

This module is the "official" provider of registries.

To ensure true singleton-ness, all registries should be acquired from this
module, by calling :func:`request` (see below).

'''

from __future__ import unicode_literals, division

from ..helpers.misc import smartstr

__all__ = ['request',
           ]


def request(name, autocreate=False, nodup=True, *args, **kwargs):
    '''

    Returns a registry dict instance specified by ``name``, optionally
    creating one for you if the requested registry does not exist.

    If the auto-creation behavior is turned off (which is the default), a
    :exc:`KeyError` will be ``raise``\ d if the requested registry does not
    exist.

    To avoid getting an existing registry when you actually want a new one,
    a parameter ``nodup`` is added to indicate that any attempt to request
    a pre-existing registry with ``autocreate=True`` should result in an
    :exc:`AttributeError` (the same exception as a registry would ``raise``
    in such a situation). The parameter defaults to ``True``; it has no
    effect if ``autocreate == False``.

    '''

    # an extra layer of input type guarantee... is it needed?
    name = smartstr(name)

    if autocreate and nodup and name in _registries:
        raise AttributeError("the registry '%s' already exists" % name)

    try:
        return _registries[name]
    except KeyError:
        pass

    if not autocreate:
        raise KeyError("requested registry %s does not exist" %
                (name, )
                )

    # instantiate, insert and return
    new_registry = _registries[name] = {}
    return new_registry


# init at module load
_registries = {}


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
