#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / object-nonrelational mapper / base model
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

from __future__ import unicode_literals, division

__all__ = [
        'Document',
        ]

from functools import partial

from .. import db_hub
from . import mapper_hub


class Document(dict):
    # only struct id is needed here, database association is done in
    # configuration file
    struct_id = None

    def __init__(self, pk=None, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.pk = pk

    def insert(self, version=None, *args, **kwargs):
        # Only continue if the class is configured to associate with a
        # struct id. Make the potential error explicit, then get a value
        # to stick with, removing possible TICTTOU vulnerability
        assert self.struct_id is not None
        struct_id = self.struct_id

        # encode self into final form
        obj = mapper_hub.encode(struct_id, self, version)

        drv, bucket = mapper_hub.get_storage(struct_id)
        with drv:
            new_pk = drv.insert(bucket, obj, self.pk)
            self.pk = new_pk

    def update(self, version=None, *args, **kwargs):
        assert self.struct_id is not None
        assert self.pk is not None
        pk, struct_id = self.pk, self.struct_id

        obj = mapper_hub.encode(struct_id, self, version)
        drv, bucket = mapper_hub.get_storage(struct_id)

        with drv:
            # XXX Naive implementation: this does not perform "smart"
            # operations such as $inc or $set, only replacing the doc
            # as a whole. Future improvements may allow specifying
            # the exact operation to be carried out by calling special
            # methods of Document instance.
            drv.update(bucket, obj, pk)

    def remove(self):
        assert self.struct_id is not None
        assert self.pk is not None
        pk, struct_id = self.pk, self.struct_id

        drv, bucket = mapper_hub.get_storage(struct_id)

        with drv:
            drv.remove(bucket, pk)

    @classmethod
    def find(cls, criteria):
        assert cls.struct_id is not None
        struct_id = cls.struct_id

        drv, bucket = mapper_hub.get_storage(struct_id)
        with drv:
            cursor = drv.find(bucket, criteria)

            # yield decoded objects
            #
            # no need to pass in version here: well-formed weiyu-generated
            # documents all have version field '_V' embedded, so letting the
            # decode routine alone is just fine.
            decoder = partial(mapper_hub.decode, struct_id)
            for pk, document in cursor:
                yield decoder(pk, document)

    @classmethod
    def all(cls):
        '''Shortcut for retrieving all objects in the configured collection.

        '''

        return cls.find({})


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
