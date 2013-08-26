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

from ...helpers.metaprogramming import classproperty, classinstancemethod


class Document(dict):
    # only struct id is needed here, database association is done in
    # configuration file
    struct_id = None

    def __repr__(self):
        return b'<%s: %s>' % (
                self.struct_id,
                super(Document, self).__repr__(),
                )

    @classproperty
    def storage(cls):
        '''Get the driver-specific object for operating the underlying
        storage.

        This should be the collection object ready for operations, provided
        by the database driver.

        '''

        assert cls.struct_id is not None
        return db_hub.get_storage(cls.struct_id)

    @classinstancemethod
    def encode(self, cls, obj=None, version=None):
        '''Encode the document into a database-ready form.

        This method, and its companion :meth:`decode`, can be invoked both
        as class method and as instance method; if invoked from an instance,
        the parameter ``obj`` is ignored.

        '''

        assert cls.struct_id is not None
        return mapper_hub.encode(cls.struct_id, self or obj, version)

    @classinstancemethod
    def decode(self, cls, obj=None, version=None):
        assert cls.struct_id is not None
        return mapper_hub.decode(cls.struct_id, self or obj, version)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
