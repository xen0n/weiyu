#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db drivers / riak driver
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

u'''
Riak Driver
~~~~~~~~~~~

This is the Riak driver for ``weiyu``.

'''

from __future__ import unicode_literals, division

import riak

from .. import db_hub
from .baseclass import BaseDriver


class RiakDriver(BaseDriver):
    def __init__(self, host, port, prefix, mapred_prefix):
        super(RiakDriver, self).__init__()

        self.host, self.port, self.prefix, self.mapred_prefix = (
                host,
                port,
                prefix,
                mapred_prefix,
                )

        # TODO: Support Riak's protobuf interface
        self.conn = riak.RiakClient(
                host,
                port,
                prefix,
                mapred_prefix,
                )
        self._buckets = {}

    def start(self):
        # No-op in HTTP interface.
        pass

    def finish(self):
        # No-op in HTTP interface.
        pass

    def get_bucket(self, bucket):
        try:
            return self._buckets[bucket]
        except KeyError:
            b = self.conn.bucket(bucket)
            self._buckets[bucket] = b

        return self._buckets[bucket]


@db_hub.register_handler('riak')
def riak_handler(
        hub,
        host='127.0.0.1',
        port=8098,
        prefix='riak',
        mapred_prefix='mapred',
        ):
    return RiakDriver(host, port, prefix, mapred_prefix)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
