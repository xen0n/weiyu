#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db / package
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

__all__ = [
        'Hub',
        ]

from ..registry.classes import UnicodeRegistry
from ..registry.provider import request

HANDLERS_KEY = 'drivers'


class DatabaseHub(object):
    # TODO: refactor this and RenderHub to use common helper code

    def __init__(self):
        self._reg = request(
                'weiyu.db',
                autocreate=True,
                klass=UnicodeRegistry,
                )

        if HANDLERS_KEY not in self._reg:
            self._reg[HANDLERS_KEY] = {}

    def register_handler(self, typ):
        def _decorator_(fn):
            self._reg[HANDLERS_KEY] = fn
            return fn
        return _decorator_

    def get_database(self, typ, *args, **kwargs):
        factory_func = self._reg[HANDLERS_KEY][typ]
        return factory_func(*args, **kwargs)


Hub = DatabaseHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
