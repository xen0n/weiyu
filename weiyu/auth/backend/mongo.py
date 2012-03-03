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

from __future__ import unicode_literals, division

import pymongo

_DuplicateKeyError = pymongo.errors.DuplicateKeyError

from .baseclass import AuthBackendBase
from .exc import NotConnectedError, AlreadyConnectedError

DATABASE_NAME = u'auth'
COLLECTION_ROLES = u'roles'
COLLECTION_USERS = u'users'

FIELD_ROLE_NAME = u'_id'
FIELD_ROLE_CAPS = u'c'

class MongoAuthBackend(AuthBackendBase):
    def __init__(self, host='localhost', port=27017, is_replica=False):
        super(MongoAuthBackend, self).__init__()

        self.host, self.port = host, port
        self._conn_type = (pymongo.ReplicaSetConnection
                           if is_replica
                           else pymongo.Connection
                           )
        self.connection = None

    def _chk_conn(self):
        if self.connection is None:
            raise NotConnectedError

    def _chk_disconn(self):
        if self.connection is not None:
            raise AlreadyConnectedError

    def _post_connect(self):
        cnn = self.connection
        auth_db = cnn[DATABASE_NAME]
        self.roles_collection = auth_db[COLLECTION_ROLES]
        self.users_collection = auth_db[COLLECTION_USERS]

    def _pre_disconnect(self):
        self.roles_collection = self.users_collection = None

    def connect(self):
        # XXX Atomicity needs to be guaranteed!!
        self._chk_disconn()

        self.connection = self._conn_type(self.host, self.port)
        self._post_connect()

    def disconnect(self):
        # XXX Atomicity!!
        self._chk_conn()

        self._pre_disconnect()
        self.connection.close()
        self.connection = None

    def __enter__(self):
        self._chk_disconn()
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def _init_idx(self):
        self._chk_conn()

        self.roles_collection.ensure_index(FIELD_ROLE_CAPS)

    def get_role(self, name):
        self._chk_conn()

        name = unicode(name)
        doc = self.roles_collection.find_one({FIELD_ROLE_NAME: name})

        if doc is None:
            raise ValueError(u"No role named '%s'" % name)
        return doc

    def get_roles_iter(self, names=None):
        self._chk_conn()

        if names is None:
            # return all roles
            cursor = self.roles_collection.find(None, {FIELD_ROLE_NAME: 1})
            return ((item[FIELD_ROLE_NAME], item[FIELD_ROLE_CAPS], )
                    for item in cursor
                    )
        else:
            # names is a list or str...
            # TODO
            raise NotImplementedError

    def get_roles(self, *args, **kwargs):
        return [i for i in self.get_roles_iter(*args, **kwargs)]

    def add_role(self, name, caps=[]):
        self._chk_conn()

        name = unicode(name)
        doc = {FIELD_ROLE_NAME: name, FIELD_ROLE_CAPS: caps, }

        # do the insertion with uniqueness checked
        try:
            self.roles_collection.insert(doc, safe=True)
        except _DuplicateKeyError:
            raise ValueError(u"Role '%s' already exists!" % name)

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
            raise ValueError(u"No role named '%s' was found", role)

        return qr[FIELD_ROLE_CAPS]

    def set_role_caps(self, role, caps):
        self._chk_conn()

        role = unicode(role)

        if issubclass(caps, unicode):
            caps = [caps]
        else:
            if issubclass(caps, str):
                caps = [unicode(caps)]

        caps = list(caps)

        # TODO


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
