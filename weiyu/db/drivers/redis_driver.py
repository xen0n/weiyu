#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db drivers / redis driver
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

'''
Redis Driver
~~~~~~~~~~~

This is the Redis driver for ``weiyu``.

Note that the "db ordinal" is used as bucket names, and not specified
in the connection parameters.

'''

from __future__ import unicode_literals, division

import redis

from .. import db_hub
from .baseclass import BaseDriver


class RedisDriver(BaseDriver):
    def __init__(self, host, port):
        super(RedisDriver, self).__init__()

        self.host, self.port = host, port
        self._buckets = {}

    def start(self):
        # No-op.
        pass

    def finish(self):
        # No-op.
        pass

    def get_bucket(self, bucket):
        try:
            return self._buckets[bucket]
        except KeyError:
            b = redis.StrictRedis(self.host, self.port, bucket)
            self._buckets[bucket] = b

        return self._buckets[bucket]

    def __repr__(self):
        return b'<weiyu.db/redis: %s:%d>' % (self.host, self.port, )


@db_hub.register_handler('redis')
def redis_handler(
        hub,
        host='127.0.0.1',
        port=6379,
        ):
    return RedisDriver(host, port)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
