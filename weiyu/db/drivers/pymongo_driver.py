#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db drivers / pymongo driver
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
``pymongo`` Database Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the MongoDB driver written for ``weiyu``, using ``pymongo``.

'''

from __future__ import unicode_literals, division

from functools import wraps

import pymongo
_DuplicateKeyError = pymongo.errors.DuplicateKeyError

from .. import db_hub
from .baseclass import *
from ...helpers import PathBuilderBase, CallReflector


class CollectionPath(PathBuilderBase):
    delim = u'.'


class PymongoDriver(DBDriverBase):
    '''``pymongo`` driver class.'''

    def __init__(self, host, port, path, is_replica=False):
        '''Constructor function.

        The database is specified through the parameters ``host`` and ``port``.

        If the database to connect to is actually a replica set, set
        ``is_replica`` to ``True``.

        '''

        super(PymongoDriver, self).__init__()

        self.host, self.port, self.path = host, port, path

        # this path object can be created anytime without side effects
        self.storage = CollectionPath()

        self._conn_type = (pymongo.ReplicaSetConnection
                           if is_replica
                           else pymongo.Connection
                           )

    @ensure_disconn
    def connect(self):
        '''Connect to the database specified in constructor.

        Raises ``AlreadyConnectedError`` if connected.

        '''

        # XXX Atomicity needs to be guaranteed!!
        self.connection = self._conn_type(self.host, self.port)
        self.ops = CallReflector(
                self.connection.__getattr__(self.path),
                CollectionPath,
                )

    @ensure_conn
    def disconnect(self):
        '''Disconnect from database.

        Raises ``NotConnectedError`` if not connected.

        '''

        # XXX Atomicity!!
        self.connection.close()
        self.connection = self.ops = self.storage = None

    @ensure_disconn
    def __enter__(self):
        '''Context manager protocol function.

        This function establishes the db connection for you.

        '''

        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''Contect manager protocol function.

        Automatically closes the db connection.

        '''

        self.disconnect()


@db_hub.register_handler('pymongo')
def pymongo_handler(hub, host, port, path, is_replica):
    return PymongoDriver(host, port, path, is_replica)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
