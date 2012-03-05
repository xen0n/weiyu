#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / auth backend / MongoDB backend
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
MongoDB Authentication Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the MongoDB backend for ``weiyu``'s authentication framework.

This implementation depends on the ``pymongo`` library to talk to MongoDB
servers.

'''

from __future__ import unicode_literals, division

import pymongo

_DuplicateKeyError = pymongo.errors.DuplicateKeyError

from .baseclass import AuthBackendBase
from .exc import NotConnectedError, AlreadyConnectedError

DEFAULT_HOST, DEFAULT_PORT = 'localhost', 27017

DATABASE_NAME = 'auth'
COLLECTION_ROLES = 'roles'
COLLECTION_USERS = 'users'

FIELD_ROLE_NAME = '_id'
FIELD_ROLE_CAPS = 'c'

CAPS_UPDATE, CAPS_ADD, CAPS_REMOVE = range(3)

class MongoAuthBackend(AuthBackendBase):
    '''MongoDB authentication backend class.'''
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, is_replica=False):
        '''Constructor function.

        The database is specified through the parameters ``host`` and ``port``.

        If the database to connect to is actually a replica set, set
        ``is_replica`` to ``True``.

        '''

        super(MongoAuthBackend, self).__init__()

        self.host, self.port = host, port
        self._conn_type = (pymongo.ReplicaSetConnection
                           if is_replica
                           else pymongo.Connection
                           )
        self.connection = None

    def _chk_conn(self):
        '''Check if the database connection has already been established.

        Raises ``NotConnectedError`` if a connection object is not present.

        .. warning::
            This is an internal function, not meant for outside use. **Do not**
            use it.

        '''

        if self.connection is None:
            raise NotConnectedError

    def _chk_disconn(self):
        '''Check if the database connection has not yet been established.

        Raises ``AlreadyConnectedError`` if a connection object is present.

        .. warning::
            This is an internal function, not meant for outside use. **Do not**
            use it.

        '''

        if self.connection is not None:
            raise AlreadyConnectedError

    def _post_connect(self):
        '''Post-connect initialization routine.

        .. warning::
            This is an internal function, not meant for outside use. **Do not**
            use it.

        '''

        cnn = self.connection
        auth_db = cnn[DATABASE_NAME]
        self.roles_collection = auth_db[COLLECTION_ROLES]
        self.users_collection = auth_db[COLLECTION_USERS]

    def _pre_disconnect(self):
        '''Pre-disconnect cleaning routine.

        .. warning::
            This is an internal function, not meant for outside use. **Do not**
            use it.

        '''

        self.roles_collection = self.users_collection = None

    def connect(self):
        '''Connect to the auth database specified in constructor.

        Raises ``AlreadyConnectedError`` if connected.

        '''

        # XXX Atomicity needs to be guaranteed!!
        self._chk_disconn()

        self.connection = self._conn_type(self.host, self.port)
        self._post_connect()

    def disconnect(self):
        '''Disconnect from database.

        Raises ``NotConnectedError`` if not connected.

        '''

        # XXX Atomicity!!
        self._chk_conn()

        self._pre_disconnect()
        self.connection.close()
        self.connection = None

    def __enter__(self):
        '''Context manager protocol function.

        This function establishes the db connection for you.
        
        '''

        self._chk_disconn()
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''Contect manager protocol function.

        Automatically closes the db connection.

        '''

        self.disconnect()

    def _init_idx(self):
        '''Ensures proper indexing of relevant fields.

        Meant to be called from initialization routines.

        '''

        self._chk_conn()

        self.roles_collection.ensure_index(FIELD_ROLE_CAPS)

    def get_role(self, name):
        '''Get details of a role named ``name``.

        Raises ``ValueError`` if the requested role does not exist.
        '''

        self._chk_conn()

        name = unicode(name)
        doc = self.roles_collection.find_one({FIELD_ROLE_NAME: name})

        if doc is None:
            raise ValueError("No role named '%s'" % name)
        return doc

    def get_roles_iter(self, names=None):
        '''Get an iterator over the roles specified in ``names``.

        If ``names`` is ``None`` (the default value), the entire list of roles
        is returned. Otherwise only those roles whose name is in ``names`` are
        returned.

        '''

        self._chk_conn()

        if names is None:
            # return all roles
            cursor = self.roles_collection.find(None)
            return ((item[FIELD_ROLE_NAME], item[FIELD_ROLE_CAPS], )
                    for item in cursor
                    )
        else:
            # names is a list or str...
            # TODO
            raise NotImplementedError

    def get_roles(self, *args, **kwargs):
        '''Get a list of roles.

        Usage is exactly the same as ``get_roles_iter`` except the return value
        is a plain old list rather than genexpr.

        '''

        return [i for i in self.get_roles_iter(*args, **kwargs)]

    def add_role(self, name, caps=[]):
        '''Add a role named ``name``, with capabilities ``caps``.

        ``caps`` should be a list of ``unicode``'s, naming the desired
        capabilities, if any.

        '''

        self._chk_conn()

        name = unicode(name)
        doc = {FIELD_ROLE_NAME: name, FIELD_ROLE_CAPS: caps, }

        # do the insertion with uniqueness checked
        try:
            self.roles_collection.insert(doc, safe=True)
        except _DuplicateKeyError:
            raise ValueError("Role '%s' already exists!" % name)

    def get_role_caps(self, role):
        self._chk_conn()

        # coerce to plain unicode in case of things like smartstr or fail
        # before hitting db
        role = unicode(role)

        qr = self.roles_collection.find_one({FIELD_ROLE_NAME: role},
                                            {FIELD_ROLE_NAME: 0,
                                             FIELD_ROLE_CAPS: 1,
                                             })
        if qr is None:
            raise ValueError("No role named '%s'", role)

        return qr[FIELD_ROLE_CAPS]

    def set_role_caps(self, role, caps, mode=CAPS_UPDATE):
        self._chk_conn()

        role = unicode(role)

        if issubclass(type(caps), unicode):
            caps = [caps]
        else:
            if issubclass(type(caps), str):
                caps = [unicode(caps)]

        caps = list(caps)

        # generate query doc
        if mode == CAPS_UPDATE:
            doc = {'$set': {FIELD_ROLE_CAPS: caps}, }
        elif mode == CAPS_ADD:
            doc = {'$addToSet': {FIELD_ROLE_CAPS: {'$each': caps}}, }
        elif mode == CAPS_REMOVE:
            doc = {'$pullAll': {FIELD_ROLE_CAPS: caps}}
        else:
            raise ValueError('Invalid mode -- use CAPS_{UPDATE,ADD,REMOVE}')

        # hit db
        self.roles_collection.update({FIELD_ROLE_NAME: role}, doc)

    def add_role_caps(self, role, caps):
        return self.set_role_caps(role, caps, CAPS_ADD)

    def remove_role_caps(self, role, caps):
        return self.set_role_caps(role, caps, CAPS_REMOVE)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
