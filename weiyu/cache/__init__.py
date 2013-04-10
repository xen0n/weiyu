#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / cache / package
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
        'cache_hub',
        ]

from ..helpers.hub import BaseHub
from ..registry.classes import UnicodeRegistry

CACHE_DRIVERS_KEY = 'drivers'
CACHE_CONF_KEY = 'caches'
DEFAULT_CACHE_NAME = 'main'


class CacheHub(BaseHub):
    registry_name = 'weiyu.cache'
    registry_class = UnicodeRegistry
    handlers_key = CACHE_DRIVERS_KEY

    def __init__(self):
        super(CacheHub, self).__init__()

        self._cfg = {}

    def get_cache(self, name=DEFAULT_CACHE_NAME):
        try:
            drv, opts = self._cfg[name]
        except KeyError:
            try:
                opts = self._reg[CACHE_CONF_KEY][name].copy()
            except KeyError:
                raise ValueError("cache '%s' not configured" % (name, ))

            drv = opts.pop('driver')
            self._cfg[name] = (drv, opts, )

        return self.do_handling(drv, opts)


cache_hub = CacheHub()


# Force loading of cache backends
from . import _reg
del _reg


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
