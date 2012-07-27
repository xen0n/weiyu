#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db / package
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

__all__ = [
        'db_hub',
        'mapper_hub',
        ]

from ..helpers.hub import BaseHub
from ..registry.classes import UnicodeRegistry
from ..registry.provider import request


class DatabaseHub(BaseHub):
    registry_name = 'weiyu.db'
    registry_class = UnicodeRegistry
    handlers_key = 'drivers'

    def __init__(self, *args, **kwargs):
        super(DatabaseHub, self).__init__(*args, **kwargs)

        # register an empty database dict if it isn't there
        if 'databases' not in self._reg:
            self._reg['databases'] = {}

    def get_database(self, name):
        # only fetch resource by name
        # NOTE: args and kwargs are removed for the moment; we'll see if
        # they're really necessary for the "flexibility" they're supposed
        # to provide.
        return self.do_handling('__name', name)


db_hub = DatabaseHub()


# reference-by-name handler
@db_hub.register_handler('__name')
def name_resolver(hub, name):
    dbconf = request('weiyu.db')
    # NOTE: exception is not caught as any request for an unmentioned
    # database SHOULD fail
    db_cfg = dbconf['databases'][unicode(name)]

    # driver type and kwargs for constructing db object
    drv_type = db_cfg['driver']
    drv_kwargs = db_cfg['options']

    return hub.do_handling(drv_type, **drv_kwargs)


# expose document mapper here to prevent circular dependency
from .mapper import mapper_hub


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
