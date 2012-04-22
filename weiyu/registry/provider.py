#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / central registry / service provider singleton
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
Central provider of registries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is the "official" provider of registry instances. To ensure a
singleton pattern, all registries should be acquired from this module.

'''

from __future__ import unicode_literals, division

from .classes import RegistryRegistry, RegistryBase

__all__ = ['request',
           ]


def request(name, autocreate=False, klass=None, *args, **kwargs):
    '''

    Returns a registry instance specified by ``name``, optionally creates
    one of type ``klass`` for you (with extra arguments passed as arguments
    to ``klass.__init__``), if no registry with name ``name`` exists.

    If the auto-creation behavior is turned off (which is the default), a
    ``KeyError`` will be ``raise``\ d. If auto-creation is enabled but
    ``klass`` is not derived from ``RegistryBase``, ``TypeError`` will be
    raised.

    '''

    # an extra layer of type guarantee... is it needed?
    name = unicode(name)

    try:
        return _registries[name]
    except KeyError:
        pass

    if not autocreate:
        raise KeyError("requested registry %s does not exist" %
                (name, )
                )

    # create one registry, but only instantiate klass iff klass is
    # RegistryBase-derived, to prevent unneeded object creation.
    if not issubclass(klass, RegistryBase):
        raise TypeError("class '%s' not subclass of RegistryBase" %
                (repr(klass), )
                )

    # instantiate, insert and return
    new_registry = klass(*args, **kwargs)
    _registries.register(name, new_registry)

    # in case of future expansion of registration semantics and possible
    # post-processing, return via the central registry singleton.
    return _registries[name]


# init at module load
_registries = RegistryRegistry()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
