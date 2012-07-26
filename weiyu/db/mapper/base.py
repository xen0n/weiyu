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

from .. import db_hub
from . import mapper_hub


class Document(dict):
    # only struct id is needed here, database association is done in
    # configuration file
    struct_id = None

    def insert(self, version=None):
        # Only continue if the class is configured to associate with a
        # struct id
        if self.struct_id is None:
            return

        # encode self into final form
        obj = mapper_hub.encode(self.struct_name, self, version)

        # get a working database connection
        conn, path = mapper_hub.get_storage(self.struct_id)

        with conn:
            conn.ops.insert(path, obj)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
