#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db drivers / pymongo driver
#
# Copyright (C) 2012-2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
``pymongo`` Database Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the MongoDB driver written for ``weiyu``, using ``pymongo``.

'''

from __future__ import unicode_literals, division

from functools import wraps

import pymongo

from .. import db_hub
from .baseclass import BaseDriver


class PymongoDriver(BaseDriver):
    '''``pymongo`` driver class.'''

    def __init__(
            self,
            path,
            host,
            port,
            is_replica,
            max_pool_size,
            tz_aware,
            ):
        '''Constructor function.

        The database server is specified through the parameters ``host`` and
        ``port``; individual database is selected by ``path``.

        If the database to connect to is actually a replica set, set
        ``is_replica`` to ``True``. This will make the connection a
        ``MongoReplicaSetClient`` instead of ``MongoClient``.

        Other parameters have the same meanings as in PyMongo.

        '''

        super(PymongoDriver, self).__init__()

        self.host, self.port, self.path = host, port, path
        self.max_pool_size, self.tz_aware = max_pool_size, tz_aware

        _conn_type = (pymongo.MongoReplicaSetClient
                           if is_replica
                           else pymongo.MongoClient
                           )
        self.conn = _conn_type(
                host=host,
                port=port,
                max_pool_size=max_pool_size,
                tz_aware=tz_aware,
                auto_start_request=False,
                )
        self.db = self.conn[self.path]
        self._buckets = {}

    def start(self):
        self.conn.start_request()

    def finish(self):
        self.conn.end_request()

    def get_bucket(self, bucket):
        try:
            return self._buckets[bucket]
        except KeyError:
            b = getattr(self.db, bucket)
            self._buckets[bucket] = b

        return self._buckets[bucket]

    def __repr__(self):
        return b'<weiyu.db/pymongo: %s:%d, path=%s>' % (
                self.host,
                self.port,
                self.path,
                )


@db_hub.register_handler('pymongo')
def pymongo_handler(
        hub,
        path,
        host='127.0.0.1',
        port=27017,
        is_replica=False,
        max_pool_size=10,
        tz_aware=False,
        ):
    return PymongoDriver(
            path,
            host,
            port,
            is_replica,
            max_pool_size,
            tz_aware,
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
