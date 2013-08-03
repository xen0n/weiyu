#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / cache drivers / redis driver
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

import redis

from ...db import db_hub
from .. import cache_hub
from .baseclass import BaseCache


class RedisCache(BaseCache):
    def __init__(self, storage):
        super(RedisCache, self).__init__()

        # XXX: Very primitive persistent connection impl
        # This relies on the Redis driver's internal state-lessness
        # The driver's start() and finish() methods will NOT be called
        self._conn = storage.driver.get_bucket(storage.bucket)

    def get(self, k):
        return self._conn.get(k)

    def set(self, k, v, timeout=None):
        return self._conn.set(k, v)

    def delete(self, k):
        return self._conn.delete(k)


@cache_hub.register_handler('redis')
def redis_handler(hub, opts):
    struct_id = opts['struct_id']
    storage = db_hub.get_storage(struct_id)

    return RedisCache(storage)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
