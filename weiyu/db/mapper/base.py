#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / object-nonrelational mapper / base model
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

from functools import partial

from .. import db_hub
from . import mapper_hub


class Document(dict):
    # only struct id is needed here, database association is done in
    # configuration file
    struct_id = None

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

        # TODO: remove this MongoDB-specific hack
        self.__assoc_id = self['_id'] if '_id' in self else None

    def insert(self, version=None, *args, **kwargs):
        # Only continue if the class is configured to associate with a
        # struct id. Make the potential error explicit, then get a value
        # to stick with, removing possible TICTTOU vulnerability
        assert self.struct_id is not None
        struct_id = self.struct_id

        # encode self into final form
        obj = mapper_hub.encode(struct_id, self, version)

        # get a working database connection
        conn, path = mapper_hub.get_storage(struct_id)

        with conn:
            # get the new id and associate self with that object
            _id = conn.ops.insert(path, obj)

        self.__assoc_id = _id

    def update(self, version=None, *args, **kwargs):
        assert self.struct_id is not None
        assert self.__assoc_id is not None
        assoc_id, struct_id = self.__assoc_id, self.struct_id
        
        obj = mapper_hub.encode(struct_id, self, version)
        conn, path = mapper_hub.get_storage(struct_id)

        with conn:
            conn.ops.update(
                    path,
                    {'_id': assoc_id, },
                    obj,
                    *args, **kwargs
                    )


    def remove(self):
        assert self.struct_id is not None
        assert self.__assoc_id is not None
        assoc_id, struct_id = self.__assoc_id, self.struct_id

        conn, path = mapper_hub.get_storage(struct_id)

        with conn:
            conn.ops.remove(path, {'_id': assoc_id, }, )

    # TODO: maybe a metaclass for inserting this into class namespace is OK
    def find(self, criteria=None, version=None, *args, **kwargs):
        assert self.struct_id is not None
        struct_id = self.struct_id

        if criteria is None:
            # use self as a criteria
            criteria = mapper_hub.encode(struct_id, self, version)

        conn, path = mapper_hub.get_storage(struct_id)

        with conn:
            cursor = conn.ops.find(path, criteria, *args, **kwargs)

            # yield decoded objects
            #
            # no need to pass in version here: well-formed weiyu-generated
            # documents all have version field '_V' embedded, so letting the
            # decode routine alone is just fine.
            decoder = partial(mapper_hub.decode, struct_id)
            for document in cursor:
                yield decoder(document)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
