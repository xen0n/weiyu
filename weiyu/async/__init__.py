#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / async / package
#
# Copyright (C) 2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

__all__ = [
        'async_hub',
        ]

from ..helpers.hub import BaseHub
from ..registry.classes import UnicodeRegistry

FLAVOR_KEY, NS_KEY = 'flavors', 'namespaces'


class AsyncHub(BaseHub):
    registry_name = 'weiyu.async'
    registry_class = UnicodeRegistry
    handlers_key = FLAVOR_KEY  # XXX currently unused

    def __init__(self):
        super(AsyncHub, self).__init__()

        if NS_KEY not in self._reg:
            self._ns = self._reg[NS_KEY] = {}

    def register_ns(self, flavor, name):
        def _decorator_(thing):
            if flavor not in self._ns:
                self._ns[flavor] = {}

            flavor_ns = self._ns[flavor]
            if name in flavor_ns:
                raise ValueError(
                        "namespace '%s' already registered" % (
                            name,
                            )
                        )

            flavor_ns[name] = thing
            return thing
        return _decorator_

    def get_namespaces(self, flavor):
        return self._ns[flavor]


async_hub = AsyncHub()

# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
