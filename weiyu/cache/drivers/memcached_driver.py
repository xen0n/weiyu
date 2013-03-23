#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / cache drivers / memcached driver
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

import memcache

from .. import cache_hub
from .baseclass import BaseCache


class MemcachedCache(BaseCache):
    def __init__(self, servers):
        super(MemcachedCache, self).__init__()
        self._conn = memcache.Client(servers)

    def get(self, k):
        return self._conn.get(k)

    def set(self, k, v, timeout=None):
        return self._conn.set(k, v)

    def delete(self, k):
        return self._conn.delete(k)


@cache_hub.register_handler('memcached')
def memcached_handler(hub, opts):
    servers = opts['servers']

    return MemcachedCache(servers)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
