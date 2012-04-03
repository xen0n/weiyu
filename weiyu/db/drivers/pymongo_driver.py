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

from .baseclass import *
from weiyu.helpers import PathBuilderBase


class CollectionPath(PathBuilderBase):
    delim = u'.'


class CallReflector(object):
    def __init__(self, target, path_type):
        self.__target = target
        self.path_type = path_type

    def __getattr__(self, att):
        def _wrapper_(path_obj, *args, **kwargs):
            if not issubclass(type(path_obj), self.path_type):
                raise ValueError(u'path object type mismatch')

            real_target = self.__target.__getattr__(unicode(path_obj))
            real_att_unbound = real_target.__class__.__dict__[att]

            if not hasattr(real_att_unbound, '__call__'):
                raise AttributeError(u"'%s' attribute is not callable" % att)

            return real_att_unbound(real_target, *args, **kwargs)

        return _wrapper_


class PymongoDriver(DBDriverBase):
    '''``pymongo`` driver class.'''

    def __init__(self, host, port, name, is_replica=False):
        '''Constructor function.

        The database is specified through the parameters ``host`` and ``port``.

        If the database to connect to is actually a replica set, set
        ``is_replica`` to ``True``.

        '''

        super(PymongoDriver, self).__init__()

        self.host, self.port, self.name = host, port, name
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
        self.storage = CollectionPath()
        self.ops = CallReflector(
                self.connection.__getattr__(self.name),
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



# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
