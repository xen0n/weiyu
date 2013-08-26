#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db / package
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
        'db_hub',
        'mapper_hub',
        ]

import six

from ..helpers.hub import BaseHub
from ..helpers.misc import smartstr
from ..helpers.modprober import ModProber
from ..registry.classes import UnicodeRegistry
from ..registry.provider import request

DBCONF_KEY, DRVOBJ_KEY = 'databases', 'drvobjs'
STORAGE_KEY, STORAGE_CACHE_KEY = 'storage', '_storage_cache'

PROBER = ModProber('weiyu.db.drivers', '%s_driver')


class DatabaseHub(BaseHub):
    registry_name = 'weiyu.db'
    registry_class = UnicodeRegistry
    handlers_key = 'drivers'

    def __init__(self, *args, **kwargs):
        super(DatabaseHub, self).__init__(*args, **kwargs)

        self._drvobjs = self._reg[DRVOBJ_KEY] = {}
        self._storage_cache = self._reg[STORAGE_CACHE_KEY] = {}

    # This association MUST be done AFTER central registry is fully
    # populated with user config, or the registry mechanism will
    # prevent user config values from being loaded.
    def _init_refresh_map(self):
        # register an empty database dict if it isn't there
        if DBCONF_KEY not in self._reg:
            self._reg[DBCONF_KEY] = {}

        # and storage configuration
        if STORAGE_KEY not in self._reg:
            self._reg[STORAGE_KEY] = {}
        self._storage = self._reg[STORAGE_KEY]

    def get_database(self, name):
        # only fetch resource by name
        # NOTE: args and kwargs are removed for the moment; we'll see if
        # they're really necessary for the "flexibility" they're supposed
        # to provide.
        try:
            return self._drvobjs[name]
        except KeyError:
            drv = self.do_handling('__name', name)
            self._drvobjs[name] = drv
            return drv

    def get_storage_conf(self, name):
        # First let's do a cached lookup...
        try:
            return self._storage_cache[name]
        except KeyError:
            pass

        try:
            cfg = self._storage[name]
        except KeyError:
            raise TypeError(
            "struct id '%s' does not have storage configured" % name
            )

        if isinstance(cfg, dict):
            # custom config, pass as-is
            cfg_dict = cfg
        elif isinstance(cfg, six.string_types):
            # shorthand for the vast majority of db/bucket setup
            # the config dict is created here
            if not isinstance(cfg, six.text_type):
                cfg = cfg.decode('utf-8')

            db, bucket = cfg.split('/', 1)

            # coerce bucket param, needed e.g. by Redis
            if bucket.startswith('(int)'):
                bucket = int(bucket[5:])

            cfg_dict = {'db': db, 'bucket': bucket, }
        else:
            raise ValueError(
            "struct id '%s': Don't know how to handle config %s" % (
                name,
                repr(cfg),
                )
            )

        self._storage_cache[name] = cfg_dict
        return cfg_dict

    def get_storage(self, name):
        storage_conf = self.get_storage_conf(name)
        db_name, bucket = storage_conf['db'], storage_conf['bucket']
        drv = self.get_database(db_name)

        return drv(bucket)


db_hub = DatabaseHub()


# reference-by-name handler
# driver objects are memoized in db_hub.get_database()
@db_hub.register_handler('__name')
def name_resolver(hub, name):
    dbconf = request('weiyu.db')
    # NOTE: exception is not caught as any request for an unmentioned
    # database SHOULD fail
    db_cfg = dbconf[DBCONF_KEY][smartstr(name)]

    # driver type and kwargs for constructing db object
    drv_type = db_cfg.pop('driver')

    # import driver module
    PROBER.modprobe(drv_type)

    return hub.do_handling(drv_type, **db_cfg)


# expose document mapper here to prevent circular dependency
from .mapper import mapper_hub


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
